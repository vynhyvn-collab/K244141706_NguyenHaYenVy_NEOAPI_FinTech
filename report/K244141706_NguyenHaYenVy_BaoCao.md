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

Đồ án này đã xây dựng thành công **Hệ thống Xếp hạng & Lọc Cổ phiếu Thông minh Đa nhân tố (Smart Stock Screener & Multi-Factor Ranking Engine)** lấy **VPBankS NEO API** làm hạ tầng cung cấp dữ liệu cốt lõi (kết hợp SSI FastConnect API). Sản phẩm khai thác sâu dữ liệu vi cấu trúc thị trường (Market Microstructure), bao gồm: độ sâu sổ lệnh 3 bước giá mua - bán (Order Book Top 3 Bids/Asks), đột biến khối lượng so với trung bình 20 phiên, dòng tiền mua/bán ròng của khối ngoại và động lượng giá trong ngày. 

Sản phẩm được đóng gói hoàn chỉnh bằng ngôn ngữ Python, áp dụng mô hình chấm điểm tổng hợp (Composite Multi-Factor Score: 0 – 100), phân tầng tín hiệu định lượng (*Top Buy, Accumulation, Neutral, Caution*) và giao diện bảng điều khiển tương tác trực quan Streamlit. Toàn bộ mã nguồn đạt chuẩn module hóa cao, tích hợp bộ kiểm soát tần suất Rate Limiter (5 requests/giây) và vượt qua 100% các bài kiểm thử tự động (Unit Tests) với Pytest.

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
Sản phẩm được thiết kế theo mô hình phân tầng chặt chẽ (Clean Layered Architecture), đảm bảo tính độc lập và khả năng mở rộng:

```
[ NGUỒN DỮ LIỆU CỐT LÕI ]
VPBankS NEO API (REST & Realtime Stream) ──► (Bổ trợ: SSI FastConnect Data)
                         │
                         ▼
[ LỚP KẾT NỐI & DỮ LIỆU (src/neo_api/) ]
- Token Bucket Rate Limiter (5 req/s)
- Session & JWT Auth Manager
- Fallback & Offline Mock Generator Engine
                         │
                         ▼
[ LỚP LOGIC TÀI CHÍNH (src/finance/) ]
- Tính toán Độ lệch Cung - Cầu Sổ lệnh (OBI)
- Tính toán Đột biến Khối lượng (Relative Volume)
- Đo lường Vị thế Động lượng Giá (Range Position)
- Đo lường Tác động Dòng tiền Khối ngoại (Foreign Net Impact)
                         │
                         ▼
[ LỚP MÔ HÌNH PHÂN TÍCH (src/analytics/) ]
- Chuẩn hóa Z-Score / Min-Max (0 - 100)
- Trọng số hóa Đa nhân tố (Composite Factor Scoring)
- Phân tầng khuyến nghị (Top Buy, Accumulation, Neutral, Caution)
- Sinh thuyết minh định lượng tự động
                         │
                         ▼
[ LỚP GIAO DIỆN SẢN PHẨM (src/app/) ]
- Bảng lọc Realtime Screener
- Scatter Plot OBI vs Biến động Giá
- Biểu đồ Đột biến Khối lượng TB20
- Biểu đồ Radar 4 Trục Nhân tố
- Thanh đo Tỷ lệ Cung/Cầu Top 3 Bids/Asks
                         │
                         ▼
[ NGƯỜI DÙNG: Nhà đầu tư / Chuyên viên phân tích ]
```

### 3.2. Lựa chọn công nghệ & Lý do
* **Python 3.14:** Ngôn ngữ hàng đầu trong FinTech và phân tích dữ liệu định lượng.
* **Pydantic & Pydantic-Settings:** Ép kiểu dữ liệu nghiêm ngặt, tự động validate cấu trúc trả về từ API và bảo mật biến môi trường.
* **Streamlit & Plotly:** Giúp xây dựng giao diện Dashboard thời gian thực, tương tác mượt mà và trực quan hóa dữ liệu đa chiều mà không làm cồng kềnh hệ thống.
* **Pytest:** Đảm bảo toàn bộ logic tài chính và kết nối được kiểm thử tự động, tái lập kết quả dễ dàng.

---

## 4. KHAI THÁC DỮ LIỆU VPBANKS NEO API & QUY TRÌNH KỸ THUẬT

### 4.1. Các Endpoint & Trường dữ liệu sử dụng
Theo tài liệu kỹ thuật chính thức của VPBankS NEO API, hệ thống khai thác các trường dữ liệu quan trọng sau:
* **Nhóm dữ liệu cổ phiếu (`/market/stock-detail/{symbol}`):**
  * `referencePrice`, `ceilingPrice`, `floorPrice`: Giá tham chiếu, trần, sàn theo quy định HOSE (+/- 7%).
  * `openPrice`, `highPrice`, `lowPrice`, `lastPrice`: Giá mở cửa, cao nhất, thấp nhất và giá khớp gần nhất.
  * `totalVol`, `totalVal`: Tổng khối lượng và giá trị khớp lệnh tích lũy trong ngày.
* **Nhóm dữ liệu vi cấu trúc Sổ lệnh (Order Book 3 Levels):**
  * `bidPrice1`, `bidVol1`, `bidPrice2`, `bidVol2`, `bidPrice3`, `bidVol3`: 3 mức giá và khối lượng đặt mua tốt nhất.
  * `askPrice1`, `askVol1`, `askPrice2`, `askVol2`, `askPrice3`, `askVol3`: 3 mức giá và khối lượng đặt bán tốt nhất.
* **Nhóm dữ liệu Giao dịch Khối ngoại (Foreign Trading):**
  * `foreignBuyVol`, `foreignSellVol`: Khối lượng mua và bán của nhà đầu tư nước ngoài.
  * `totalRoom`, `currentRoom`: Tổng room và tỷ lệ sở hữu nước ngoài còn lại.

### 4.2. Quản lý Tần suất gọi API (Rate Limiting)
NEO API quy định giới hạn nghiêm ngặt **5 requests/giây** cho mỗi máy khách. Để tuân thủ nguyên tắc sử dụng hạ tầng có trách nhiệm (Mục 4 đề thi), lớp `src/neo_api/client.py` đã cài đặt thuật toán **Token Bucket Rate Limiter**:
* Bể chứa (Bucket) có sức chứa tối đa 5 tokens, được nạp đầy theo tốc độ 5 tokens/giây.
* Mỗi yêu cầu gọi API bắt buộc phải lấy được token trước khi phát yêu cầu HTTP. Nếu bể hết token, thuật toán tự động tính toán thời gian trễ và `sleep` chính xác cho đến khi có token khả dụng, tuyệt đối không làm tắc nghẽn dịch vụ của VPBankS.

### 4.3. Cơ chế Dự phòng (Offline Fallback Engine)
Để phục vụ việc kiểm thử, chạy tự động ngoài giờ giao dịch hoặc khi giảng viên chấm bài ngoại tuyến, Client hỗ trợ chế độ `NEO_ENVIRONMENT=MOCK`. Bộ sinh dữ liệu mô phỏng chân thực:
* Tuân thủ bước giá 100đ / 500đ và biên độ sàn HOSE (+/- 7%).
* Dữ liệu sổ lệnh Top 3 Bids/Asks phản ánh đúng tương quan cung - cầu vi cấu trúc.
* Tự động chuyển đổi mượt mà giữa LIVE và MOCK mà không làm gián đoạn ứng dụng.

### 4.4. Quy chuẩn Dấu thời gian
Toàn bộ dấu thời gian đều được lưu trữ và trình bày nhất quán theo múi giờ Việt Nam: `Asia/Ho_Chi_Minh` (UTC+7).

---

## 5. PHƯƠNG PHÁP TÀI CHÍNH & CƠ SỞ MÔ HÌNH ĐỊNH LƯỢNG

Mô hình phân tích của đồ án dựa trên sự kết hợp giữa **Lý thuyết Vi cấu trúc Thị trường (Market Microstructure)** và **Mô hình Xếp hạng Đa nhân tố (Multi-Factor Scoring Model)**.

### 5.1. Nhân tố 1: Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI)
* **Cơ sở học thuật:** Theo nghiên cứu của Cartea & Jaimungal (2014) và Stoikov (2018), tỷ lệ chênh lệch giữa khối lượng đặt mua và đặt bán tại các bước giá tốt nhất là chỉ báo dự báo hướng đi của giá trong ngắn hạn có độ tin cậy cao nhất.
* **Công thức tính toán:**
  $$OBI = \frac{\sum_{i=1}^3 \text{BidVol}_i - \sum_{i=1}^3 \text{AskVol}_i}{\sum_{i=1}^3 \text{BidVol}_i + \sum_{i=1}^3 \text{AskVol}_i} \in [-1.0, 1.0]$$
* **Ý nghĩa:**
  * $OBI > +0.2$: Lực Cầu gom mua áp đảo -> Dự báo áp lực tăng giá ngắn hạn.
  * $OBI < -0.2$: Lực Cung bán đè áp đảo -> Dự báo áp lực giảm giá ngắn hạn.

### 5.2. Nhân tố 2: Đột biến Khối lượng (Relative Volume - RelVol)
* **Cơ sở học thuật:** Lý thuyết Khối lượng (Volume Spread Analysis - VSA) khẳng định giá tăng mà không có khối lượng hỗ trợ là tín hiệu suy yếu (Bẫy giá tăng). Giá tăng đi kèm khối lượng đột biến chứng tỏ có sự tham gia của dòng tiền lớn (Smart Money).
* **Công thức tính toán:**
  $$\text{RelVol} = \frac{\text{TotalVolume}}{\text{AvgVolume}_{20\text{d}}}$$
* **Ý nghĩa:** $\text{RelVol} \ge 1.3\text{x}$ phản ánh thanh khoản tăng đột biến, giúp hấp thụ rủi ro trượt giá (Slippage risk).

### 5.3. Nhân tố 3: Tác động Dòng tiền Nước ngoài (Foreign Net Impact)
* **Cơ sở học thuật:** Tại thị trường chứng khoán Việt Nam, nhà đầu tư nước ngoài đóng vai trò dẫn dắt tâm lý mạnh mẽ, đặc biệt trong nhóm VN30.
* **Công thức tính toán:**
  $$\text{Foreign Impact} = \frac{\text{Foreign Net Value}}{\text{Total Value}} = \frac{\text{Foreign Buy Value} - \text{Foreign Sell Value}}{\text{Total Traded Value}}$$

### 5.4. Nhân tố 4: Động lượng Giá (Price Momentum & Range Position)
* **Công thức tính toán:**
  $$\text{Range Position} = \frac{\text{Last Price} - \text{Low Price}}{\text{High Price} - \text{Low Price}} \in [0.0, 1.0]$$
* **Ý nghĩa:** Khi vị thế gần 1.0, cổ phiếu đang giao dịch ở mức cao nhất ngày, chứng tỏ bên mua hoàn toàn kiểm soát cuộc chơi.

### 5.5. Thuật toán Xếp hạng Tổng hợp (Composite Multi-Factor Score)
Từng nhân tố được chuẩn hóa về thang điểm $0 - 100$ ($S_{\text{Mom}}, S_{\text{Liq}}, S_{\text{For}}, S_{\text{OBI}}$). Điểm tổng hợp được tính theo phương pháp bình quân trọng số cân bằng:
$$\text{Composite Score} = 0.25 \times S_{\text{Mom}} + 0.25 \times S_{\text{Liq}} + 0.25 \times S_{\text{For}} + 0.25 \times S_{\text{OBI}}$$

### 5.6. Ma trận Phân tầng Khuyến nghị (Ranking Tiers)
* **Top Buy ($\ge 70$ điểm):** Đồng thuận cao giữa Lực gom Cung-Cầu ($OBI > 0$), Khối ngoại mua ròng và Đột biến thanh khoản.
* **Accumulation ($55 - <70$ điểm):** Cổ phiếu đang được tích lũy âm thầm.
* **Neutral ($40 - <55$ điểm):** Trạng thái thị trường giằng co, cân bằng.
* **Caution ($< 40$ điểm):** Cổ phiếu chịu áp lực bán đè hoặc khối ngoại xả mạnh.

---

## 6. TRIỂN KHAI SẢN PHẨM & GIAO DIỆN NGƯỜI DÙNG

Sản phẩm được xây dựng dưới dạng Web Dashboard hiện đại với 4 phân khu chức năng:
1. **Sidebar Bộ lọc Chiến lược:** Cho phép lọc tức thì theo nhóm phân hạng (*Top Buy*), ngưỡng điểm, điều kiện $OBI > 0$, đột biến Vol và Khối ngoại.
2. **Khu vực Chỉ số Thị trường (Top Metrics):** Thống kê độ rộng thị trường (Số mã tăng/giảm), tổng giá trị mua ròng khối ngoại và số lượng mã đạt chuẩn Top Buy.
3. **Tab 1 - Bảng lọc Realtime:** Danh sách xếp hạng cổ phiếu trực quan với định dạng màu sắc nổi bật và thuyết minh tín hiệu tự động.
4. **Tab 2 - Trực quan hóa Vi cấu trúc:** 
   * Biểu đồ phân tán Scatter OBI vs % Biến động giá.
   * Biểu đồ thanh ngang so sánh đột biến thanh khoản so với TB20 phiên.
5. **Tab 3 - Soi kèo Chi tiết từng mã:** 
   * Biểu đồ Radar 4 nhân tố đánh giá toàn diện sức mạnh cổ phiếu.
   * Bảng chi tiết 3 mức giá Mua/Bán và thanh tiến trình tỷ lệ lực Cầu Mua vs Cung Bán.
6. **Tab 4 - Thuyết minh Phương pháp & Miễn trừ trách nhiệm:** Giải thích công thức và lưu ý rủi ro.

---

## 7. THIẾT KẾ KIỂM THỬ & KẾT QUẢ KIỂM CHỨNG

### 7.1. Kế hoạch kiểm thử tự động
Dự án thiết lập bộ kiểm thử đơn vị tự động trong thư mục `tests/` sử dụng `pytest`:
* `tests/test_neo_api.py`: Kiểm thử cơ chế xác thực JWT, tính hợp lệ của cấu trúc Pydantic Models, giá trần/sàn HOSE và danh sách rổ VN30.
* `tests/test_finance_ranking.py`: Kiểm thử tính toán độc lập công thức OBI, Relative Volume và thuật toán tính điểm tổng hợp.

### 7.2. Kết quả kiểm chứng
Chạy lệnh kiểm thử:
```powershell
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe -v
```
Kết quả ghi nhận:
```
tests/test_finance_ranking.py::test_calculate_order_book_imbalance PASSED [ 16%]
tests/test_finance_ranking.py::test_calculate_relative_volume PASSED     [ 33%]
tests/test_finance_ranking.py::test_multi_factor_ranking_engine PASSED   [ 50%]
tests/test_neo_api.py::test_neo_client_authentication PASSED             [ 66%]
tests/test_neo_api.py::test_get_stock_snapshot_structure PASSED          [ 83%]
tests/test_neo_api.py::test_get_market_universe_vn30 PASSED              [100%]
============================== 6 passed in 0.82s ==============================
```
**Tỷ lệ đạt: 6/6 test cases (100% Passed).**

---

## 8. GIỚI HẠN MÔ HÌNH & QUY TẮC SỬ DỤNG CÓ TRÁCH NHIỆM

### 8.1. Giới hạn mô hình & Dữ liệu
* **Hiện tượng Lệnh ảo (Order Book Spoofing):** Dữ liệu 3 bước giá phản ánh ý chí đặt lệnh tại thời điểm hiện tại, tuy nhiên các lệnh chờ lớn có thể bị hủy đột ngột trước khi khớp lệnh. Do đó, OBI cần kết hợp chặt chẽ với khối lượng khớp lệnh thực tế ($RelVol$).
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
1. Nắm vững kỹ thuật thu thập, chuẩn hóa dữ liệu tài chính thời gian thực và quản trị giới hạn tần suất API.
2. Xây dựng và kiểm chứng thành công mô hình định lượng đa nhân tố vi cấu trúc sổ lệnh (OBI).
3. Đóng gói sản phẩm phần mềm FinTech hoàn chỉnh, giao diện tương tác cao, mã nguồn an toàn và kiểm thử chặt chẽ.

---

## PHỤ LỤC: TỪ ĐIỂN DỮ LIỆU CỐT LÕI

| Tên trường dữ liệu | Kiểu dữ liệu | Mô tả tài chính |
| :--- | :--- | :--- |
| `symbol` | `str` | Mã chứng khoán (VD: FPT, HPG, TCB) |
| `last_price` | `float` | Giá khớp gần nhất (VNĐ) |
| `order_book_imbalance` | `float` | Độ lệch Cung - Cầu sổ lệnh vi cấu trúc $[-1.0, 1.0]$ |
| `relative_volume` | `float` | Tỷ lệ khối lượng so với TB 20 phiên ($RelVol$) |
| `foreign_net_value` | `float` | Giá trị mua/bán ròng của khối ngoại (VNĐ) |
| `foreign_net_impact` | `float` | Tỷ lệ mua ròng khối ngoại trên tổng thanh khoản |
| `composite_score` | `float` | Điểm xếp hạng tổng hợp đa nhân tố ($0.0 - 100.0$) |
| `ranking_tier` | `str` | Phân tầng tín hiệu: *Top Buy, Accumulation, Neutral, Caution* |

*(Hết báo cáo)*
