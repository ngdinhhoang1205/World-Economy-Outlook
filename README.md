# 📊 World Economy Monitor — Global Macroeconomic Dashboard

This project tracks **core macroeconomic indicators across ~100+ countries**, organized into **4 pillars**, through a Python/Jupyter ETL pipeline (`source.ipynb` + `utils.py` + `config.py`) feeding a Power BI report (`World Economy Monitor.pbip`).

---

## 🚀 Framework Overview (4 Pillars)

| Pillar | Focus | Goal |
| :--- | :--- | :--- |
| **Pillar 1** | 📈 **System Health & Growth** | Identify the economic cycle (expansion vs. recession) |
| **Pillar 2** | 🏦 **Inflation & Monetary Policy** | Track price pressure and investment flow direction |
| **Pillar 3** | 🛒 **Labor & Consumption** | Assess real consumer purchasing power |
| **Pillar 4** | 🌐 **Trade & Supply Chain** | Measure trade flows and geopolitical shocks |

---

## 📌 Indicators & Data Sources

Data comes from two pipelines:
- **DBnomics** (`dbnomics` Python package) — a free aggregator that mirrors IMF/OECD/BIS/World Bank series.
- **Direct IMF API** (`api.imf.org`, SDMX 3.0) — IMF's own data platform, used where DBnomics' mirror has gaps or lag. Requires a free API key from `portal.api.imf.org`, stored in `.env` as `IMF_API_KEY` (see [Setup](#-setup)).

### 📈 Pillar 1: System Health & Growth

* **1. Real GDP** (local currency, converted to USD via exchange rate)
  * **Source:** DBnomics — `IMF/IFS` (`NGDP_XDC`), merged with `IMF/IFS` exchange rate series (`EDNA_USD_XDC_RATE`) for USD conversion.
* **2. Industrial Production Index (IPI)**
  * **Source:** Dual — **primary**: direct IMF API, `IMF.STA:PI` dataflow (indicator `IND`, index level). **Fallback**: DBnomics `IMF/IFS` (`AIP_IX`) for the ~15 countries the IMF PI dataflow doesn't cover (e.g. UK, Belgium, Sweden). Each row is tagged with a `Source` column so both are traceable in the combined dataset.

### 🏦 Pillar 2: Inflation & Monetary Policy

* **3. Headline Consumer Price Index (CPI)**
  * **Source:** DBnomics — `IMF/CPI` (`PCPI_IX`, monthly).
* **4. Central Bank Policy Rates**
  * **Source:** DBnomics — `BIS/WS_CBPOL` (daily policy rates for major central banks: Fed, ECB, BOJ, PBOC, etc.).

### 🛒 Pillar 3: Labor & Consumption

* **5. Unemployment Rate**
  * **Source:** DBnomics — `IMF/WEO:latest` (`LUR`, % of total labor force).
* **6. Retail Sales Growth**
  * **Source:** DBnomics — `OECD/MEI` (`SLRTTO02`, monthly retail trade value).
* **7. Population** *(added — not in the original 9-indicator scope, used for per-capita metrics)*
  * **Source:** Direct IMF API — `IMF.RES:WEO` dataflow (indicator `LP`). Includes IMF forecast years alongside actuals.

### 🌐 Pillar 4: Trade & Supply Chain

* **8. Merchandise Imports / Exports**
  * **Source:** Direct IMF API — `IMF.STA:IMTS` dataflow (formerly *Direction of Trade Statistics / DOT*). Exports use `XG_FOB_USD`; imports try `MG_FOB_USD` first and fall back to `MG_CIF_USD` per-country (most countries only report imports on a CIF basis). Fetched bilaterally (by real ISO3 counterpart country, chunked to stay under the API's URL-length limit) and summed — **not** via `COUNTERPART_COUNTRY=*`, which pulls in regional aggregate codes (`G001`, `GX170`, etc.) that would double-count totals.
  * *Migrated from DBnomics' `IMF/DOT` mirror, which only had usable coverage for ~6 countries.*
* **9. Trade in Services** *(added — not in the original 9-indicator scope)*
  * **Source:** Direct IMF API — `IMF.STA:BOP` (Balance of Payments) dataflow, indicator `S` (Services), credits (`CD_T`) for exports / debits (`DB_T`) for imports. No bilateral breakdown (BOP reports each country vs. rest-of-world). Quarterly, evenly split into monthly for consistency with the goods-trade series.
* **10. Global Manufacturing PMI**
  * **Source:** DBnomics — `OECD/MEI` (`BSCICP02`, Business Confidence Index).
* **11. Commodity Price Index**
  * **Status:** ⚠️ Not yet implemented (placeholder cell only). Planned source: `WB` (World Bank Pink Sheet) or `IMF` (`IFS`/PCP) via DBnomics.

### 🇺🇸 US Deep-Dive (supplementary, outside the 4-pillar framework)

* CPI, Unemployment Rate, Nonfarm Payrolls, Real GDP, Manufacturing Investment — sourced directly from **FRED** (Federal Reserve Economic Data) via `pandas_datareader`.

### 🗺️ Country Reference Data

* **Country/continent mapping**: built locally from `config.py` (`dict_2_char`/`dict_3_char`, ~108 countries) — no external API. Continent is assigned offline via the `pycountry_convert` library, with manual overrides for the handful of codes it doesn't recognize (historical entities like the former USSR, special territories).

---

## 🧩 Setup

1. Install dependencies: `pandas`, `dbnomics`, `requests`, `python-dotenv`, `pycountry-convert`, `pandas_datareader`, `matplotlib`.
2. Register a free account at `portal.api.imf.org`, subscribe to the Data API product, and get your subscription key.
3. Create a `.env` file in the project root (already git-ignored):
   ```
   IMF_API_KEY=your_key_here
   ```
4. Run `source.ipynb` top to bottom to regenerate all CSVs under `data/`.

---

## 📊 Power BI Report (`World Economy Monitor.pbip`)

The report has **9 pages** — all 5 content pages built, plus 4 drill-through tooltip pages.

| Page | Status | Visuals |
| :--- | :--- | :--- |
| **Overview** | ✅ Built | KPI cards (Trade Balance, Imports, Exports — goods only; GDP, YoY/MoM CPI, Unemployment, IPI, Retail Sales, Central Bank Policy Rate), a Current/Previous Month & Year summary table, and a Country slicer |
| **Economic Growth** | ✅ Built | Map of GDP by country, bar chart of IPI growth rate by country, GDP treemap, YoY GDP line chart over time, GDP combo chart (per-capita + growth rate), with Nation / Date / Continent slicers |
| **Inflation & Monetary Policy** | ✅ Built | Bar chart of YoY CPI by country, line chart of YoY CPI over time, bar chart of central bank policy rate by country, line chart of policy rate over time, with Nation / Date / Continent slicers |
| **Labor & Consumption** | ✅ Built | Line chart of retail sales over time, population treemap by country, line chart of unemployment rate over time, with Nation / Date / Continent slicers |
| **Global Trade** | ✅ Built | Column chart of goods trade balance by year (Import/Export tooltip), column chart of services trade balance by year (Import/Export tooltip), ribbon chart of export value by top counterpart countries over time, with Nation and Date slicers |
| **GDP_Tooltip** | ✅ Built | Drill-through table: GDP by country |
| **YoY_GDP_Tooltip** | ✅ Built | Drill-through line chart: GDP over years |
| **MoM_policyrate_Tooltip** | ✅ Built | Drill-through line chart: policy rate over years |
| **Country_IPI_Trend_Tooltip** | ✅ Built | Drill-through line chart: IPI trend by country |

### Sample Screenshots

**Overview**
![Overview page](images/Overview-sample.png)

**Economic Growth**
![Economic Growth page](images/Economic-Growth.png)

**Inflation & Monetary Policy**
![Inflation & Monetary Policy page](images/Inflation-and-monetary-policy.png)

**Global Trade**
![Global Trade page](images/Global-Trade-sample.png)

### Semantic Model

Key fact tables loaded into the model: `f_gross_domestic_product`, `f_industrial_production_index`, `f_consumer_price_index`, `f_cb_policy_rates`, `f_unemployment_rate`, `f_retail_sales`, `f_PMI`, `f_trade_balance`, `f_imf_imports_goods`, `f_imf_exports_goods`, `f_imf_imports_services`, `f_imf_exports_services`, `imf_population`, plus `d_country` and `d_calendar` as dimension tables and a central `Measures_Table` for DAX measures.
