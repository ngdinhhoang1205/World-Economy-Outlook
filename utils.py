import os
import re
import pandas as pd
import requests
from dbnomics import fetch_series
from dotenv import load_dotenv

load_dotenv()

IMF_API_BASE = "https://api.imf.org/external/sdmx/3.0/data/dataflow"
IMF_STRUCTURE_BASE = "https://api.imf.org/external/sdmx/3.0/structure/codelist"


# IMF regional-department groupings that are (unhelpfully) coded as plain 3-letter
# IDs, so they pass a naive [A-Z]{3} filter alongside real ISO3 country codes.
_IMTS_REGIONAL_CODES = {"AFR", "EUR", "APD", "MCD", "WHD"}


def get_imts_countries(agency="IMF.STA", codelist_id="CL_IMTS_COUNTRY", version="1.0.0"):
    """
    Real ISO3 reporting countries for the IMTS dataflow, straight from IMF's public
    codelist (no API key needed) — excludes regional/grouping aggregates like G001,
    GX170, TX799, U019 (which all contain digits) and the handful of IMF regional
    departments (AFR, EUR, APD, MCD, WHD) that are coded as plain 3-letter IDs.
    """
    resp = requests.get(
        f"{IMF_STRUCTURE_BASE}/{agency}/{codelist_id}/{version}",
        params={"detail": "full"},
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    codes = resp.json()["data"]["codelists"][0]["codes"]
    return sorted(
        c["id"] for c in codes
        if re.fullmatch(r"[A-Z]{3}", c["id"]) and c["id"] not in _IMTS_REGIONAL_CODES
    )


def _parse_imf_sdmx_json(payload):
    """Flatten an SDMX-JSON 3.0 data message (api.imf.org) into a DataFrame."""
    structure = payload["data"]["structures"][0]
    series_dims = structure["dimensions"]["series"]
    time_values = [v["value"] for v in structure["dimensions"]["observation"][0]["values"]]

    rows = []
    for series_key, series in payload["data"]["dataSets"][0].get("series", {}).items():
        dim_indexes = [int(i) for i in series_key.split(":")]
        dim_values = {
            dim["id"]: dim["values"][idx]["id"]
            for dim, idx in zip(series_dims, dim_indexes)
        }
        for obs_index, obs in series.get("observations", {}).items():
            rows.append({**dim_values, "period": time_values[int(obs_index)], "value": obs[0]})

    df = pd.DataFrame(rows)
    if not df.empty:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def chunked(items, size=150):
    """Split a list into chunks — IMF's API rejects a key with all ~260 countries joined by '+' (400 Bad Request)."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def fetch_imf_api(dataflow_id, key, agency="IMF.STA", version="+", start_period=None, end_period=None, api_key=None):
    """
    Fetch data directly from IMF's new SDMX 3.0 API (api.imf.org), bypassing DBnomics.
    Requires a subscription key from portal.api.imf.org (pass explicitly or set IMF_API_KEY env var).

    key : SDMX dot-separated dimension key, e.g. "VNM.MG_FOB_USD.G001.M" for IMTS.
    """
    api_key = api_key or os.environ["IMF_API_KEY"]
    url = f"{IMF_API_BASE}/{agency}/{dataflow_id}/{version}/{key}"
    params = {
        "dimensionAtObservation": "TIME_PERIOD",
        "attributes": "all",
        "measures": "all",
        "includeHistory": "true",
    }
    if start_period or end_period:
        bound = f"ge:{start_period}" if start_period else ""
        bound += f"+le:{end_period}" if end_period else ""
        params["c[TIME_PERIOD]"] = bound

    resp = requests.get(
        url,
        params=params,
        headers={"Accept": "application/json", "Ocp-Apim-Subscription-Key": api_key},
    )
    resp.raise_for_status()
    return _parse_imf_sdmx_json(resp.json())


def fetch_bop_services(entry, countries, unit="USD", frequency="Q", start_period=None, end_period=None, api_key=None):
    """
    Fetch BOP trade-in-services value ('CD_T' credits = exports, 'DB_T' debits = imports)
    for a list of countries. Unlike IMTS, BOP has no counterpart-country dimension — each
    country reports one total against the rest of world — so no bilateral chunking or
    aggregate-code filtering is needed, only chunking the reporting-country list itself.
    """
    dfs = []
    for chunk in chunked(countries):
        key = f"{'+'.join(chunk)}.{entry}.S.{unit}.{frequency}"
        dfs.append(fetch_imf_api(
            dataflow_id="BOP", key=key,
            start_period=start_period, end_period=end_period, api_key=api_key,
        ))
    dfs = [df for df in dfs if not df.empty]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def fetch_imts(indicator, country_key="*", frequency="M", start_period=None, end_period=None, api_key=None):
    """
    Fetch an IMTS indicator (e.g. MG_FOB_USD, MG_CIF_USD, XG_FOB_USD) across every real
    bilateral counterpart country, chunked to stay under the API's URL-length limit.
    Uses get_imts_countries() instead of a '*' wildcard on COUNTERPART_COUNTRY so
    regional/grouping aggregates (G001, GX170, ...) never enter the result — summing
    this DataFrame's 'value' per COUNTRY/period gives the correct total, no double-counting.
    """
    dfs = []
    for chunk in chunked(get_imts_countries()):
        key = f"{country_key}.{indicator}.{'+'.join(chunk)}.{frequency}"
        dfs.append(fetch_imf_api(
            dataflow_id="IMTS", key=key,
            start_period=start_period, end_period=end_period, api_key=api_key,
        ))
    dfs = [df for df in dfs if not df.empty]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def fetch_imf_data(country_dict, dataset_code="IFS", metric_suffix="PCPI_IX", frequency="M"):
    """Fetch macroeconomic data from the IMF via DBnomics with dynamic dataset mapping.

    Parameters:
    -----------
    country_dict : dict
        A dictionary containing country codes (keys) and display names (values).
    dataset_code : str
        The IMF dataset code on DBnomics. 'CPI' for inflation only, 'IFS' for general macro data.
    metric_suffix : str
        The specific IMF metric code (e.g., 'NGDP_R_XDC', 'LUR_P_PE_NUM').
    frequency : str
        Data frequency: 'M' (Monthly), 'Q' (Quarterly), 'A' (Annual).
    """
    all_dfs = []

    for code, country_name in country_dict.items():
        # Tạo endpoint chính xác dựa trên dataset_code
        series_id = f"IMF/{dataset_code}/{frequency}.{code}.{metric_suffix}"

        try:
            df = fetch_series(series_id)
            df["country_name"] = country_name
            df["country_code"] = code
            all_dfs.append(df)
        except Exception as e:
            # Nếu chạy IFS bị lỗi (một số nước nộp dữ liệu trễ), hệ thống sẽ log ra để kiểm tra
            print(f"Error {country_name} ({series_id}): {e}")

    if all_dfs:
        
        return pd.concat(all_dfs, ignore_index=True)
    else:
        print("No data was successfully loaded.")
        return pd.DataFrame()
    

def fetch_imf_bulk(dataset_code="IFS", metric_code="NGDP_R_XDC", frequency="Q", country_list=None):
    """
    Cào dữ liệu vĩ mô từ IMF bằng phương pháp lọc Dimension của DBnomics.
    Tránh lỗi nối chuỗi ID sai cấu trúc.
    """
    print(f"--- Đang tải dữ liệu cho mã: {metric_code} ({frequency}) ---")
    
    # Thiết lập bộ lọc kích thước (Dimensions) theo chuẩn API DBnomics
    # FREQ: Tần suất (M, Q, A)
    # INDICATOR: Mã chỉ số vĩ mô của IMF
    if dataset_code=="WEO:2025-04" and metric_code=="LUR":
        dimensions = {
            # "freq": [frequency],
            "weo-subject": [metric_code],
            "unit": 'pcent'
        }
        
        # Nếu người dùng truyền vào danh sách mã nước cụ thể (ví dụ: ['VN', 'US', 'DE'])
        if country_list:
            dimensions["weo-country"] = country_list
    else:
        dimensions = {
            "FREQ": [frequency],
            "INDICATOR": [metric_code]
        }
        
        # Nếu người dùng truyền vào danh sách mã nước cụ thể (ví dụ: ['VN', 'US', 'DE'])
        if country_list:
            dimensions["REF_AREA"] = country_list

    try:
        # Gọi API tải hàng loạt theo bộ lọc
        df = fetch_series(provider_code="IMF", dataset_code=dataset_code, dimensions=dimensions)
        
        if df.empty:
            print(f"⚠️ Không tìm thấy dữ liệu nào khớp với mã {metric_code}.")
            return pd.DataFrame()
            
        # Chuẩn hóa lại tên cột để đồng bộ với cấu trúc Power BI của bạn
        # DBnomics trả về cột 'REF_AREA' làm mã quốc gia và 'Reference Area' làm tên quốc gia
        df = df.rename(columns={
            "REF_AREA": "country_code",
            "Reference Area": "country_name",
            "period": "Date"
        })
        
        # Chỉ giữ lại các cột cốt lõi cần thiết cho Dashboard
        core_columns = ["Date", "value", "country_code", "country_name"]
        df = df[[col for col in core_columns if col in df.columns]]
        
        print(f"✅ Tải thành công {len(df)} dòng dữ liệu!")
        return df

    except Exception as e:
        print(f"❌ Lỗi hệ thống khi gọi API: {e}")
        return pd.DataFrame()