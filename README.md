# ĐỒ ÁN CUỐI KỲ: BỘ LỌC CỔ PHIẾU THÔNG MINH (NEO API FINTECH)
### Smart Stock Screener & Multi-Factor Microstructure Ranking Engine

* **Trường:** Đại học Kinh tế - Luật (UEL) - Đại học Quốc gia TP.HCM  
* **Khoa:** Tài chính - Ngân hàng  
* **Học phần:** Gói phần mềm ứng dụng cho tài chính 1 (Mã lớp: 261BFF401101 / 261BFF401102)  
* **Sinh viên thực hiện:** Nguyễn Hà Yến Vy  
* **MSSV:** K244141706  
* **Nền tảng hạ tầng cốt lõi:** VPBankS NEO API (kết hợp SSI FastConnect API)  

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY NHANH TRONG 1 DÒNG LỆNH

Dự án đã được tự động hóa hoàn toàn. Người chấm chỉ cần mở PowerShell tại thư mục dự án và chạy:

### Chạy Dashboard ứng dụng trực tiếp:
```powershell
$env:PYTHONPATH="."; .\.venv\Scripts\streamlit.exe run src/app/main.py
```
*(Trình duyệt sẽ tự động khởi động tại `http://localhost:8501`)*

### Chạy toàn bộ kiểm thử tự động (Unit Tests):
```powershell
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe -v
```

---

## 📖 GIỚI THIỆU DỰ ÁN

Dự án giải quyết bài toán cốt lõi của nhà đầu tư cá nhân và chuyên viên phân tích trên thị trường chứng khoán Việt Nam: **"Làm thế nào để nhận diện sớm cổ phiếu tiềm năng ngay trong phiên giao dịch dựa trên vi cấu trúc dòng tiền thay vì chỉ nhìn vào biến động giá chậm chạp?"**

Sản phẩm xây dựng **Mô hình Xếp hạng Đa nhân tố (Multi-Factor Microstructure Ranking Engine)** khai thác sâu dữ liệu thời gian thực từ **VPBankS NEO API**:
1. **Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI):** Khai thác 3 mức giá Mua/Bán tốt nhất từ sổ lệnh khớp lệnh liên tục.
2. **Đột biến Thanh khoản (Relative Volume - RelVol):** Đo lường áp lực khối lượng so với trung bình 20 phiên.
3. **Dòng tiền Khối ngoại (Foreign Net Flow Impact):** Đo lường mức độ gom/xả ròng và tỷ trọng nâng đỡ thị trường của khối ngoại.
4. **Động lượng Giá (Price Momentum & Intra-day Range Position):** Phản ánh sức mạnh giá duy trì đến cuối phiên.

---

## 🏗️ KIẾN TRÚC HỆ THỐNG
Chuỗi xử lý dữ liệu tuân thủ chuẩn kiến trúc Mục 5 của đề thi:
```
VPBankS NEO API (REST & Realtime Stream)
       │ (Top 3 Bids/Asks, Ticker, Foreign Trade)
       ▼
[src/neo_api/] ──► Client kết nối, Token Bucket Rate Limiter (5 req/s), Retry Backoff, Fallback Engine
       │
[src/finance/] ──► Tính toán chỉ báo vi cấu trúc: OBI, RelVol, Price Momentum, Foreign Net Impact
       │
[src/analytics/] ► Chuẩn hóa Min-Max, Thuật toán Composite Multi-Factor Scoring (0 - 100), Phân tầng tín hiệu
       │
[src/app/] ──────► Dashboard tương tác Streamlit: Screener Realtime, Radar Chart, OBI Scatter, Order Depth
       │
    NGƯỜI DÙNG (Nhà đầu tư / Chuyên viên phân tích)
```

---

## 🔒 AN TOÀN, BẢO MẬT & QUY TẮC SỬ DỤNG HẠ TẦNG

1. **Bảo mật tuyệt đối:** Mã nguồn không chứa bất kỳ khóa truy cập, mật khẩu hay token cá nhân nào. Mọi cấu hình đều được quản lý độc lập qua tệp `.env` (mẫu tại `.env.example`).
2. **Chế độ MOCK / LIVE linh hoạt:** Mặc định hệ thống chạy chế độ `NEO_ENVIRONMENT=MOCK` (với dữ liệu vi cấu trúc mô phỏng chân thực theo đúng biên độ 7% sàn HOSE, giá bước nhảy, khối ngoại và Top 3 Bids/Asks) giúp người chấm bài có thể thẩm định dự án ngoại tuyến 24/7 mà không phụ thuộc vào giờ mở cửa thị trường. Khi có API Key thật, chỉ cần đổi `NEO_ENVIRONMENT=LIVE`.
3. **Tuân thủ Rate Limit:** Tích hợp bộ điều phối tốc độ `Token Bucket RateLimiter` giới hạn nghiêm ngặt **5 requests/giây**, bảo vệ hạ tầng NEO API theo đúng quy định của VPBankS.
4. **Không giao dịch tiền thật:** Dự án tuân thủ nghiêm ngặt Mục 8 của đề thi, không phát sinh bất kỳ lệnh mua/bán thật nào.

---

## 📂 CẤU TRÚC THƯ MỤC NGUỒN
```
D:\K244141706_NguyenHaYenVy_NEOAPI_FinTech\
├── README.md                      # Tài liệu tổng quan & hướng dẫn chạy nhanh
├── requirements.txt               # Danh mục thư viện phụ thuộc
├── .env.example                   # Tệp mẫu cấu hình bảo mật
├── report/
│   └── MSSV_HoTen_BaoCao.md       # Báo cáo cuối kỳ 10 chương chuẩn mực
├── src/
│   ├── neo_api/
│   │   ├── config.py              # Pydantic Settings & Quản lý biến môi trường
│   │   ├── models.py              # Pydantic Data Models (Snapshot, OrderBook, FactorScores)
│   │   └── client.py              # NEO API Client, Token Bucket Rate Limiter & Fallback Engine
│   ├── finance/
│   │   └── indicators.py          # Bộ tính toán chỉ báo vi cấu trúc: OBI, RelVol, Momentum, Foreign
│   ├── analytics/
│   │   └── ranking.py             # Động cơ Xếp hạng đa nhân tố, Composite Score & Phân tầng tín hiệu
│   └── app/
│       └── main.py                # Dashboard tương tác Streamlit (Bảng lọc, Radar, Scatter OBI)
└── tests/
    ├── test_neo_api.py            # Kiểm thử kết nối, Rate Limit & Cấu trúc dữ liệu
    └── test_finance_ranking.py    # Kiểm thử tính toán công thức OBI, RelVol & Xếp hạng (100% Passed)
```
