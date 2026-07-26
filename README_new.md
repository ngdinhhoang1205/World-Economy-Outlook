# 📊 Trụ Cột Chỉ Số Kinh Tế Vĩ Mô Toàn Cầu (Macroeconomic Dashboard Pillars)

Tài liệu này tổng hợp **9 chỉ số vĩ mô cốt lõi** được chia thành **4 trụ cột chính**, kèm theo gợi ý các nguồn dữ liệu tối ưu nhất trên **DBnomics** phục vụ cho luồng ETL và trực quan hóa trên Power BI / Dashboard.

---

## 🚀 Tổng Quan 4 Trụ Cột (Framework Summary)

| Trụ cột | Tên gọi | Mục tiêu theo dõi |
| :--- | :--- | :--- |
| **Trụ cột 1** | 📈 **Sức khỏe & Tăng trưởng** | Nhận diện chu kỳ kinh tế (Mở rộng hay Suy thoái) |
| **Trụ cột 2** | 🏦 **Lạm phát & Tiền tệ** | Theo dõi áp lực giá & định hướng dòng vốn đầu tư |
| **Trụ cột 3** | 🛒 **Lao động & Tiêu dùng** | Đánh giá sức mua thực tế của người tiêu dùng |
| **Trụ cột 4** | 🌐 **Giao thương & Chuỗi cung ứng** | Đo lường dòng chảy thương mại & cú sốc địa chính trị |

---

## 📌 Chi Tiết Các Trụ Cột & Nguồn Dữ Liệu DBnomics

### 📈 Trụ cột 1: Sức khỏe & Tăng trưởng Hệ thống (Economic Growth)
> *Nhóm này giúp theo dõi nền kinh tế thế giới đang mở rộng hay tiến sát nguy cơ suy thoái.*

*   **1. Real GDP Growth (`YoY %` hoặc `QoQ %`)**
    *   **Ý nghĩa:** Tốc độ tăng trưởng tổng sản phẩm quốc nội thực tế.
    *   **Nguồn DBnomics tối ưu:** `IMF` (Bộ dữ liệu *WEO - World Economic Outlook*) hoặc `OECD`.
*   **2. Industrial Production Index - IPI**
    *   **Ý nghĩa:** Chỉ số Sản xuất Công nghiệp — chỉ báo nhanh phản ánh sức khỏe ngành chế tạo toàn cầu trước khi số liệu GDP (vốn có độ trễ lớn) được công bố.
    *   **Nguồn DBnomics tối ưu:** `OECD` (Bộ dữ liệu *KEI - Main Economic Indicators*) hoặc `Eurostat` (Khu vực Châu Âu).

---

### 🏦 Trụ cột 2: Độ ổn định Giá cả & Chính sách Tiền tệ (Inflation & Monetary Policy)
> *Nhóm chỉ số cực kỳ nhạy cảm, trực tiếp điều hướng dòng vốn đầu tư toàn cầu.*

*   **3. Headline Consumer Price Index - CPI**
    *   **Ý nghĩa:** Lạm phát tổng thể — đo lường áp lực chi phí sinh hoạt lên người tiêu dùng.
    *   **Nguồn DBnomics tối ưu:** `IMF` (*WEO*) hoặc `OECD` (*KEI*).
*   **4. Central Bank Policy Rates**
    *   **Ý nghĩa:** Lãi suất điều hành của các Ngân hàng Trung ương lớn (FED, ECB, BOJ, PBOC). 
    *   *Lưu ý:* Lãi suất tăng $\rightarrow$ Tiền tệ thắt chặt $\rightarrow$ Kinh tế giảm nhiệt.
    *   **Nguồn DBnomics tối ưu:** `BIS` (*Bank for International Settlements*) — tổng hợp lãi suất ngân hàng trung ương cực kỳ chuẩn xác và sạch.

---

### 🛒 Trụ cột 3: Thị trường Lao động & Tiêu dùng (Labor & Consumption)
> *Sức mua của người dân thế giới phụ thuộc hoàn toàn vào trục này.*

*   **5. Unemployment Rate**
    *   **Ý nghĩa:** Tỷ lệ thất nghiệp — đo lường lượng lao động không có việc làm.
    *   **Nguồn DBnomics tối ưu:** `OECD` hoặc `ILO` (*International Labour Organization* — bao phủ toàn cầu).
*   **6. Retail Sales Growth**
    *   **Ý nghĩa:** Tăng trưởng Doanh số Bán lẻ — đại diện cho động lực tiêu dùng cá nhân ($C$), chiếm tỷ trọng lớn nhất trong quy mô GDP.
    *   **Nguồn DBnomics tối ưu:** `OECD` (*KEI*).

---

### 🌐 Trụ cột 4: Giao thương & Địa chính trị (Global Trade & Supply Chain)
> *Phần độc đáo nhất trên Dashboard toàn cầu dùng để giải thích các cú sốc (dịch bệnh, xung đột địa chính trị).*

*   **7. Global Manufacturing PMI**
    *   **Ý nghĩa:** Chỉ số Nhà quản trị Mua hàng — Chỉ báo dẫn dắt (*Leading Indicator*) quan trọng nhất.
        *   `PMI > 50`: Ngành sản xuất mở rộng.
        *   `PMI < 50`: Ngành sản xuất thu hẹp.
    *   **Nguồn DBnomics tối ưu:** Chuỗi dữ liệu PMI từ `ISM`, `OECD` (BSCI - Business Confidence) hoặc các báo cáo tổng hợp kinh tế vĩ mô.
*   **8. Merchandise Exports / Imports Growth**
    *   **Ý nghĩa:** Tăng trưởng Kim ngạch Xuất nhập khẩu — đo lường sức khỏe dòng chảy thương mại toàn cầu.
    *   **Nguồn DBnomics tối ưu:** `WTO` (*World Trade Organization*) hoặc `IMF` (Bộ dữ liệu *DOT - Direction of Trade Statistics*).
*   **9. Commodity Price Index**
    *   **Ý nghĩa:** Chỉ số Giá Hàng hóa (Dầu mỏ, Vàng, Nông sản) — phản chiếu áp lực chi phí đầu vào và rủi ro bất ổn địa chính trị.
    *   **Nguồn DBnomics tối ưu:** `WB` (*World Bank - Pink Sheet Commodity Prices*) hoặc `IMF` (*IFS/PCP*).


prob: f_gross_domestic_product: domestic currency so we have to convert to USD for standardization
resolution: EDNA_​USD_​XDC_​RATE