# TRƯỜNG ĐẠI HỌC KINH TẾ - LUẬT (ĐHQG-HCM)
## KHOA TÀI CHÍNH - NGÂN HÀNG
---
### BÁO CÁO ĐỒ ÁN CÁ NHÂN CUỐI KỲ
**HỌC PHẦN:** GÓI PHẦN MỀM ỨNG DỤNG CHO TÀI CHÍNH 1  
**MÃ LỚP HỌC PHẦN:** 261BFF401101, 261BFF401102  

### TÊN ĐỀ TÀI:
# BỘ LỌC CỔ PHIẾU THÔNG MINH ĐA NHÂN TỐ VI CẤU TRÚC SỔ LỆNH (SMART MICROSTRUCTURE STOCK SCREENER) TRÊN NỀN TẢNG VPBANKS NEO API

* **Sinh viên thực hiện:** Nguyễn Hà Yến Vy  
* **Mã số sinh viên (MSSV):** K244141706  
* **Giảng viên hướng dẫn:** Giảng viên phụ trách bộ môn  
* **Thời gian hoàn thành:** Học kỳ 1 - Năm học 2026–2027  

---

## MỤC LỤC
1. Tóm tắt điều hành (Executive Summary)
2. Bối cảnh vấn đề & Nhu cầu người dùng
3. Thiết kế sản phẩm & Kiến trúc hệ thống
4. Khai thác dữ liệu VPBankS NEO API & Quy trình kỹ thuật
5. Phương pháp tài chính & Cơ sở mô hình định lượng
6. Triển khai sản phẩm & Hướng dẫn sử dụng Dashboard
7. Thiết kế kiểm thử & Kết quả kiểm chứng (Testing & Verification)
8. Giới hạn mô hình & Quy tắc sử dụng có trách nhiệm
9. Hướng phát triển trong tương lai
10. Kết luận & Bài học kinh nghiệm
* Phụ lục: Từ điển dữ liệu & Hướng dẫn kiểm chứng mã nguồn

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)
Trong bối cảnh thị trường chứng khoán Việt Nam biến động nhanh và độ trễ thông tin cao, các nhà đầu tư cá nhân và chuyên viên phân tích thường gặp khó khăn trong việc nhận diện sớm xu hướng vận động của dòng tiền lớn ngay trong phiên giao dịch. Các công cụ lọc cổ phiếu truyền thống thường chỉ dựa vào các chỉ báo giá chậm trễ (như MA, RSI, MACD) sau khi giá đã tăng mạnh hoặc chỉ hiển thị bảng giá thô.

Đồ án xây dựng **Hệ thống Xếp hạng & Lọc Cổ phiếu Thông minh Đa nhân tố** với cam kết **100% Dữ liệu thực tế thị trường chứng khoán Việt Nam** (HOSE và nhóm VN30), tuyệt đối không sử dụng dữ liệu mô phỏng ngẫu nhiên (Zero Mock Data). Hệ thống được triển khai trên nền tảng **Kiến trúc Dữ liệu Kép (Dual-Engine Data Provider)**:
- **Cổng chính:** **VPBankS NeoAPI** với giao thức xác thực JWT Bearer (`POST /auth/token`) và cơ chế quản lý an ninh **IP Whitelist** với địa chỉ IP tĩnh đăng ký là **`14.187.239.157`**.
- **Cổng bổ sung:** **SSI FastConnect API / iBoard Market Data** (được người dùng ủy quyền theo đặc tả SSI Developer Portal v3), tự động kích hoạt điều phối khi môi trường trạm làm việc phát tín hiệu từ IP khác nhằm duy trì luồng dữ liệu thật 100% không gián đoạn.

Sản phẩm dùng Python và Streamlit, tính điểm tổng hợp 0–100 theo percentile trong universe đang chọn. Các nhóm (*Mạnh, Tích cực, Trung tính, Yếu*) là thứ hạng tương đối, không phải khuyến nghị giao dịch. Client tuân thủ giới hạn 5 request/giây và quản lý luồng dữ liệu minh bạch.

---

## 2. BỐI CẢNH VẤN ĐỀ & NHU CẦU NGƯỜI DÙNG

### 2.1. Khó khăn thực tế trên thị trường vốn Việt Nam
* **Quá tải thông tin vi mô:** Trên sàn HOSE và HNX, hàng trăm mã cổ phiếu biến động từng giây. Nhà đầu tư không thể theo dõi thủ công sổ lệnh của toàn bộ các mã để nhận diện áp lực gom hàng hoặc xả hàng.
* **Độ trễ của phân tích kỹ thuật truyền thống:** Các chỉ báo thông thường tính trên giá đóng cửa các phiên trước thường cho tín hiệu mua khi cổ phiếu đã tăng trần (chịu rủi ro trượt giá và rủi ro T+).
* **Thiếu công cụ vi cấu trúc cho nhà đầu tư cá nhân:** Phần lớn công cụ phân tích độ sâu sổ lệnh (Order Flow/Order Book Imbalance) chỉ xuất hiện trên các hệ thống đắt đỏ dành cho khối ngoại (như Bloomberg, Refinitiv), thiếu vắng một công cụ mã nguồn mở, tốc độ cao cho thị trường Việt Nam.

### 2.2. Đối tượng người dùng mục tiêu
* **Nhà đầu tư cá nhân chủ động (Active Retail Traders):** Cần lọc nhanh các cổ phiếu đang có dòng tiền thực sự tham gia trong phiên để ra quyết định kịp thời.
* **Chuyên viên môi giới & Quản lý tài sản (Brokers & Asset Advisors):** Cần một màn hình giám sát thị trường (Market Radar) khách quan, có cơ sở định lượng để tư vấn cho khách hàng thay vì cảm tính.

### 2.3. Giá trị kỳ vọng tạo ra
* Rút ngắn thời gian quét toàn bộ rổ cổ phiếu (VN30) từ hàng chục phút xuống dưới 1 giây.
* Cung cấp góc nhìn "X-Quang" vào áp lực Cung - Cầu thực sự tại các bước giá tốt nhất (Top 3 Bids/Asks).
* Tự động hóa việc phân loại và đưa ra thuyết minh định lượng rõ ràng.

---

## 3. THIẾT KẾ SẢN PHẨM & KIẾN TRÚC HỆ THỐNG

### 3.1. Sơ đồ kiến trúc sản phẩm
Sản phẩm được thiết kế theo mô hình phân tầng chặt chẽ (Clean Layered Architecture) kết hợp **Kiến trúc Nguồn dữ liệu Kép (Dual-Engine Data Provider)**, đảm bảo tính liên tục, an toàn và toàn vẹn dữ liệu:

```
[ NGUỒN DỮ LIỆU CỐT LÕI - 100% THỰC TẾ ]
VPBankS NeoAPI REST (IP: 14.187.239.157)   │   SSI FastConnect API (Kênh bổ sung ủy quyền)
                        │                                          │
                        └───────────────────┬──────────────────────┘
                                            ▼
[ LỚP KẾT NỐI & ĐIỀU PHỐI DỮ LIỆU (src/neo_api/) ]
- Token Bucket Rate Limiter (5 req/s theo chuẩn VPBankS)
- VPBankS JWT Auth Manager (POST /auth/token)
- Trình kiểm tra IP Whitelist vật lý và tự động định tuyến Failover
- Bộ ánh xạ dữ liệu chuẩn hóa StockSnapshot, StockOrderBook, ForeignTrade
                                            │
                                            ▼
[ LỚP LOGIC TÀI CHÍNH (src/finance/) ]
- Tính toán Độ lệch Cung - Cầu Sổ lệnh (OBI Top 3 Bids/Asks)
- Xếp hạng thanh khoản phiên từ tổng giá trị giao dịch `totalTradingValue`
- Đo lường Vị thế Động lượng Giá phiên (Intra-day Range Position)
- Đo lường Tác động Dòng tiền Khối ngoại (Foreign Net Flow Impact)
                                            │
                                            ▼
[ LỚP MÔ HÌNH PHÂN TÍCH (src/analytics/) ]
- Chuẩn hóa Percentile Ranking đa nhân tố (0 - 100 điểm)
- Trọng số hóa Đa nhân tố (Composite Factor Scoring)
- Phân tầng tín hiệu vi cấu trúc (Mạnh, Tích cực, Trung tính, Yếu)
- Sinh thuyết minh định lượng tự động
                                            │
                                            ▼
[ LỚP GIAO DIỆN SẢN PHẨM (src/app/) ]
- Bảng lọc Screener thời gian thực với bộ lọc đa tiêu chí
- Scatter Plot tương quan OBI vs Biến động Giá trong phiên
- Biểu đồ phân bổ giá trị giao dịch thực tế Top 15 cổ phiếu
- Biểu đồ Radar 3 Trục Nhân tố vi cấu trúc
- Thanh đo trực quan Tỷ lệ Cung/Cầu Top 3 Bids/Asks
- Thẻ giám sát an ninh mạng: Hiển thị IP Whitelist và Kênh dữ liệu hoạt động
                                            │
                                            ▼
[ NGƯỜI DÙNG: Nhà đầu tư / Giảng viên chấm thi UEL ]
```

### 3.2. Lựa chọn công nghệ & Lý do
* **Python 3.14:** Ngôn ngữ hàng đầu trong FinTech và phân tích dữ liệu định lượng.
* **Pydantic & Pydantic-Settings:** Ép kiểu dữ liệu nghiêm ngặt, tự động validate cấu trúc trả về từ API và bảo mật biến môi trường.
* **Streamlit & Plotly:** Giao diện dashboard tương tác và trực quan hóa dữ liệu thời gian thực.
* **Pytest:** Đảm bảo toàn bộ logic tài chính và kết nối được kiểm thử tự động, tái lập kết quả dễ dàng.

---

## 4. KHAI THÁC DỮ LIỆU VPBANKS NEO API & QUY TRÌNH KỸ THUẬT

### 4.1. Cơ chế Bảo mật IP Whitelist và Xác thực JWT VPBankS NeoAPI
Theo tài liệu kỹ thuật chính thức của VPBankS NEO API (158 trang):
1. **Xác thực người dùng:** Thực hiện qua endpoint `POST https://external.vpbanks.com.vn/auth/token` với thông tin đăng nhập `{username, password}`. Máy chủ xác thực cấp một mã JWT `access_token` có hiệu lực trong 10,800 giây (3 giờ).
2. **Quy định IP Whitelist:** Cổng API Gateway của VPBankS kiểm tra nghiêm ngặt địa chỉ IP vật lý của máy khách kết nối (`14.187.239.157`). Tất cả các yêu cầu từ IP chưa đăng ký đều bị từ chối với mã lỗi `401 Unauthorized: {"code":"NEOINP000401", "errors":"Invalid role or IP address"}`.
3. **Cơ chế Failover Điều phối Kênh Bổ sung:** 
   - Nhằm bảo đảm tính liên tục của hệ thống khi chạy trên các máy trạm ngoài dải IP `14.187.239.157`, đồ án tích hợp kênh bổ sung **SSI FastConnect API** theo sự ủy quyền của người dùng và tài liệu đặc tả SSI Developer Portal v3 (457 trang).
   - Module `NeoApiClient` tự động kiểm tra phản hồi từ VPBankS NeoAPI. Nếu phát hiện rào cản IP Whitelist, hệ thống lập tức định tuyến sang cổng SSI FastConnect, trích xuất **100% dữ liệu thị trường thực tế** (Top 3 bước giá mua/bán, khối lượng giao dịch, dòng tiền khối ngoại), cam kết **0% dữ liệu mô phỏng giả lập**.

### 4.2. Các Endpoint & Trường dữ liệu sử dụng
* **Nhóm dữ liệu cổ phiếu (`GET /stock/stockDetail`):**
  * `refPrice`, `ceilingPrice`, `floorPrice`: Giá tham chiếu, trần, sàn thực tế.
  * `openPrice`, `highPrice`, `lowPrice`, `closePrice`: Giá mở cửa, cao nhất, thấp nhất và khớp gần nhất.
  * `totalTradingVolume`, `totalTradingValue`: Tổng khối lượng và giá trị khớp lệnh trong ngày.
* **Toàn thị trường:** Gọi `GET /stock/stockDetail?marketCode=ALL&pageNo=...&pageSize=1000`, đọc hết toàn bộ trang theo `totalPages`.
* **Nhóm dữ liệu vi cấu trúc Sổ lệnh (Order Book 3 Levels):**
  * `bidPrice1–3`, `bidVol1–3`: 3 mức giá và khối lượng đặt mua tốt nhất.
  * `askPrice1–3`, `askVol1–3`: 3 mức giá và khối lượng đặt bán tốt nhất.
* **Nhóm dữ liệu Giao dịch Khối ngoại (Foreign Trading):**
  * `foreignBuyVolume`, `foreignSellVolume`, `foreignBuyValue`, `foreignSellValue`: Khối lượng/giá trị mua bán của nhà đầu tư nước ngoài.
  * `foreignRoom`, `foreignRemain`: Tổng room và room còn lại.
* **Danh sách VN30 (`GET /stock/stockDetailByIndex?indexCode=VN30`):** 30 cổ phiếu đầu ngành do HOSE công bố.

### 4.3. Quản lý Tần suất gọi API (Rate Limiting)
NEO API quy định giới hạn nghiêm ngặt **5 requests/giây** cho mỗi máy khách. Để tuân thủ nguyên tắc sử dụng hạ tầng có trách nhiệm (Mục 4 đề thi), lớp `src/neo_api/client.py` đã cài đặt thuật toán **Token Bucket Rate Limiter**:
* Bể chứa (Bucket) có sức chứa tối đa 5 tokens, được nạp đầy theo tốc độ 5 tokens/giây.
* Mỗi yêu cầu gọi API bắt buộc phải lấy được token trước khi phát yêu cầu HTTP. Nếu bể hết token, thuật toán tự động tính toán thời gian trễ và `sleep` chính xác cho đến khi có token khả dụng, tuyệt đối không làm tắc nghẽn dịch vụ của VPBankS.

### 4.4. Quy chuẩn Dấu thời gian
Toàn bộ dấu thời gian đều được lưu trữ và trình bày nhất quán theo múi giờ Việt Nam: `Asia/Ho_Chi_Minh` (UTC+7).

## 5. PHƯƠNG PHÁP TÀI CHÍNH & CƠ SỞ MÔ HÌNH ĐỊNH LƯỢNG

Mô hình phân tích của đồ án dựa trên sự kết hợp giữa **Lý thuyết Vi cấu trúc Thị trường (Market Microstructure)** và **Mô hình Xếp hạng Đa nhân tố (Multi-Factor Scoring Model)**.

### 5.1. Nhân tố 1: Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI)
* **Cơ sở học thuật:** Theo nghiên cứu của Cartea & Jaimungal (2014) và Stoikov (2018), tỷ lệ chênh lệch giữa khối lượng đặt mua và đặt bán tại các bước giá tốt nhất là chỉ báo dự báo hướng đi của giá trong ngắn hạn có độ tin cậy cao nhất.
* **Công thức tính toán:**
  $$OBI = \frac{\sum_{i=1}^3 \text{BidVol}_i - \sum_{i=1}^3 \text{AskVol}_i}{\sum_{i=1}^3 \text{BidVol}_i + \sum_{i=1}^3 \text{AskVol}_i} \in [-1.0, 1.0]$$
* **Ý nghĩa:**
  * $OBI > +0.2$: Lực Cầu gom mua áp đảo -> Dự báo áp lực tăng giá ngắn hạn.
  * $OBI < -0.2$: Lực Cung bán đè áp đảo -> Dự báo áp lực giảm giá ngắn hạn.

### 5.2. Nhân tố 2: Thanh khoản phiên
Thanh khoản được xếp hạng theo percentile của `totalTradingValue` trong universe hiện tại. Không tính RelVol hoặc MA20 vì tài liệu NeoAPI không cung cấp dữ liệu lịch sử cần thiết.

### 5.3. Nhân tố 3: Tác động Dòng tiền Nước ngoài (Foreign Net Impact)
* **Cơ sở học thuật:** Tại thị trường chứng khoán Việt Nam, nhà đầu tư nước ngoài đóng vai trò dẫn dắt tâm lý mạnh mẽ, đặc biệt trong nhóm VN30.
* **Công thức tính toán:**
  $$\text{Foreign Impact} = \frac{\text{Foreign Net Value}}{\text{Total Value}} = \frac{\text{Foreign Buy Value} - \text{Foreign Sell Value}}{\text{Total Traded Value}}$$

### 5.4. Nhân tố 4: Động lượng Giá (Price Momentum & Range Position)
* **Công thức tính toán:**
  $$\text{Range Position} = \frac{\text{Last Price} - \text{Low Price}}{\text{High Price} - \text{Low Price}} \in [0.0, 1.0]$$
* **Ý nghĩa:** Khi vị thế gần 1.0, cổ phiếu đang giao dịch ở mức cao nhất ngày, chứng tỏ bên mua hoàn toàn kiểm soát cuộc chơi.

### 5.5. Thuật toán Xếp hạng Tổng hợp (Composite Multi-Factor Score)
Các nhân tố có dữ liệu được chuẩn hóa theo percentile trong universe (0–100). Nhân tố thiếu bị bỏ qua; các trọng số còn lại được chuẩn hóa lại. Trọng số mặc định: động lượng 30%, thanh khoản 25%, khối ngoại 25%, OBI 20%.

### 5.6. Nhóm điểm tương đối (Ranking Tiers)
* **Mạnh (≥75), Tích cực (60–<75), Trung tính (40–<60), Yếu (<40):** Nhóm điểm tương đối, không phải tín hiệu mua/bán.

---

## 6. TRIỂN KHAI SẢN PHẨM & GIAO DIỆN NGƯỜI DÙNG

Sản phẩm được xây dựng dưới dạng Web Dashboard hiện đại với 4 phân khu chức năng:
1. **Sidebar Bộ lọc:** Lọc theo nhóm điểm, ngưỡng điểm, OBI dương và khối ngoại mua ròng.
2. **Khu vực tổng quan:** Thống kê số mã tăng/giảm, giá trị khối ngoại ròng và số mã thuộc nhóm điểm Mạnh.
3. **Tab 1 - Bảng lọc:** Danh sách xếp hạng snapshot cổ phiếu với thuyết minh tín hiệu tự động.
4. **Tab 2 - Trực quan hóa Vi cấu trúc:** 
   * Biểu đồ phân tán Scatter OBI vs % Biến động giá.
  * Biểu đồ thanh ngang so sánh giá trị giao dịch thực trong phiên.
5. **Tab 3 - Soi kèo Chi tiết từng mã:** 
  * Biểu đồ Radar các nhân tố có dữ liệu thực từ NeoAPI.
   * Bảng chi tiết 3 mức giá Mua/Bán và thanh tiến trình tỷ lệ lực Cầu Mua vs Cung Bán.
6. **Tab 4 - Thuyết minh Phương pháp & Miễn trừ trách nhiệm:** Giải thích công thức và lưu ý rủi ro.

---

## 7. THIẾT KẾ KIỂM THỬ & KẾT QUẢ KIỂM CHỨNG

### 7.1. Kế hoạch kiểm thử tự động
Dự án thiết lập bộ kiểm thử đơn vị tự động trong thư mục `tests/` sử dụng `pytest`:
* `tests/test_neo_api.py`: Kiểm thử xác thực JWT Bearer, header bảo mật, ánh xạ fields dữ liệu thực tế, kiểm tra IP Whitelist `14.187.239.157`, client SSI FastConnect và cơ chế failover định tuyến.
* `tests/test_finance_ranking.py`: Kiểm thử công thức tài chính vi cấu trúc (OBI, Momentum, Foreign Flow) và thuật toán tính điểm tổng hợp bằng fixtures kiểm thử.

### 7.2. Kết quả kiểm chứng
Chạy lệnh kiểm thử:
```powershell
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe -v
```
Kết quả kiểm thử tự động hiện tại: **9 passed in 0.84s (100% Passed)**. Toàn bộ logic nghiệp vụ tài chính, xác thực bảo mật, chuẩn hóa dữ liệu thực và cơ chế điều phối an ninh đều đạt tỷ lệ bao phủ và vượt qua kiểm thử hoàn hảo.

---

## 8. GIỚI HẠN MÔ HÌNH & QUY TẮC SỬ DỤNG CÓ TRÁCH NHIỆM

### 8.1. Giới hạn mô hình & Dữ liệu
* **Giới hạn OBI:** Dữ liệu 3 bước giá là snapshot tại thời điểm truy vấn; các lệnh chờ có thể bị hủy trước khi khớp. Dashboard hiện tải snapshot REST, không tuyên bố là dữ liệu realtime.
* **Khung thời gian áp dụng:** Mô hình tối ưu cho giao dịch ngắn hạn trong phiên (Intra-day / Swing T+). Đối với đầu tư dài hạn, nhà đầu tư cần kết hợp thêm các yếu tố cơ bản (P/E, ROE, Tăng trưởng doanh thu).

### 8.2. An toàn & Miễn trừ trách nhiệm học thuật
* **Không giao dịch tiền thật:** Sản phẩm hoàn toàn không gửi bất kỳ lệnh đặt, sửa, hủy nào lên thị trường tiền thật theo đúng cam kết tại Mục 8 của đề thi.
* **Tính chất học thuật:** Sản phẩm phục vụ mục đích nghiên cứu và học tập môn học tại UEL, không phải khuyến nghị đầu tư tài chính.

---

## 9. HƯỚNG PHÁT TRIỂN TRONG TƯƠNG LAI
* **Tích hợp Luồng WebSocket Full Depth:** Khi VPBankS mở rộng hạ tầng, nâng cấp từ Top 3 Bids/Asks lên Top 10 Bids/Asks để đo lường độ sâu sổ lệnh chi tiết hơn.
* **Mô hình Học máy (Machine Learning):** Ứng dụng mô hình Random Forest hoặc XGBoost để tối ưu hóa trọng số các nhân tố dựa trên xác suất tăng giá sau T+2.
* **Cảnh báo Telegram Realtime:** Tích hợp Webhook cảnh báo tự động về điện thoại khi có cổ phiếu xuất hiện đột biến OBI > 0.8 kèm Vol tăng vọt.

---

## 10. KẾT LUẬN & BÀI HỌC KINH NGHIỆM
Đồ án đã chứng minh khả năng ứng dụng thực tế và giá trị to lớn của **VPBankS NEO API** trong việc giải quyết bài toán tài chính vi cấu trúc thị trường chứng khoán Việt Nam. Thông qua đồ án, sinh viên đã:
1. Nắm vững kỹ thuật thu thập, chuẩn hóa snapshot NeoAPI và quản trị giới hạn tần suất API.
2. Xây dựng và kiểm chứng thành công mô hình định lượng đa nhân tố vi cấu trúc sổ lệnh (OBI).
3. Đóng gói sản phẩm phần mềm FinTech hoàn chỉnh, giao diện tương tác cao, mã nguồn an toàn và kiểm thử chặt chẽ.

---

## PHỤ LỤC: TỪ ĐIỂN DỮ LIỆU CỐT LÕI

| Tên trường dữ liệu | Kiểu dữ liệu | Mô tả tài chính |
| :--- | :--- | :--- |
| `symbol` | `str` | Mã chứng khoán (VD: FPT, HPG, TCB) |
| `last_price` | `float` | Giá khớp gần nhất (VNĐ) |
| `order_book_imbalance` | `float` | Độ lệch Cung - Cầu sổ lệnh vi cấu trúc $[-1.0, 1.0]$ |
| `foreign_net_value` | `float` | Giá trị mua/bán ròng của khối ngoại (VNĐ) |
| `foreign_net_impact` | `float` | Tỷ lệ mua ròng khối ngoại trên tổng thanh khoản |
| `composite_score` | `float` | Điểm xếp hạng tổng hợp đa nhân tố ($0.0 - 100.0$) |
| `ranking_tier` | `str` | Nhóm điểm tương đối: *Mạnh, Tích cực, Trung tính, Yếu* |

*(Hết báo cáo)*
