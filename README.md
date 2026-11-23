# ĐỒ ÁN CUỐI KỲ: BỘ LỌC CỔ PHIẾU THÔNG MINH (NEO API FINTECH)
### Smart Stock Screener & Multi-Factor Microstructure Ranking Engine

* **Trường:** Đại học Kinh tế - Luật (UEL) - Đại học Quốc gia TP.HCM  
* **Khoa:** Tài chính - Ngân hàng  
* **Học phần:** Gói phần mềm ứng dụng cho tài chính 1 (Mã lớp: 261BFF401101 / 261BFF401102)  
* **Sinh viên thực hiện:** Nguyễn Hà Yến Vy  
* **MSSV:** K244141706  
* **Nền tảng dữ liệu:** VPBankS NeoAPI & SSI FastConnect API (100% Dữ liệu thực tế, 0% Mock)  
* **Bảo mật:** IP Whitelist được đọc từ biến môi trường, không công khai trong kho mã nguồn.  

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

Sản phẩm xây dựng **Mô hình Xếp hạng Đa nhân tố (Multi-Factor Microstructure Ranking Engine)** với cam kết **100% Dữ liệu thị trường thực tế**, vận hành theo kiến trúc kép:
1. **Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI):** Khai thác 3 mức giá Mua/Bán tốt nhất từ sổ lệnh khớp lệnh liên tục.
2. **Thanh khoản trong phiên:** Xếp hạng theo giá trị giao dịch thực tế `totalTradingValue` nhằm lọc các mã có dòng tiền hoạt động mạnh.
3. **Dòng tiền Khối ngoại (Foreign Net Flow Impact):** Đo lường mức độ gom/xả ròng và tỷ trọng nâng đỡ thị trường của khối ngoại.
4. **Động lượng Giá (Price Momentum & Intra-day Range Position):** Phản ánh sức mạnh giá duy trì đến cuối phiên.

---

## 🏗️ KIẾN TRÚC HỆ THỐNG DUAL-ENGINE

Chuỗi xử lý dữ liệu tuân thủ chuẩn kiến trúc Mục 5 của đề thi kết hợp cơ chế định tuyến thông minh:
```
           ┌────────────────────────────────────────────────────────┐
           │     KIẾN TRÚC NGUỒN DỮ LIỆU KÉP (DUAL-ENGINE)          │
           │                                                        │
           │   [Cổng Chính]                    [Cổng Bổ Sung]       │
           │   VPBankS NeoAPI                  SSI FastConnect API  │
           │   (Cấu hình bí mật)               (Ủy quyền người dùng) │
           └──────────┬─────────────────────────────────┬───────────┘
                      │                                 │
                      ▼                                 ▼
         [src/neo_api/client.py & src/neo_api/ssi_client.py]
         │ (Xác thực qua biến môi trường, định tuyến dữ liệu 100% Thật)
         ▼
    [Chuẩn hóa/Lưu trữ: Pydantic + StockSnapshot]
    │ (Chuẩn hóa phản hồi thành models; cache phiên trong bộ nhớ)
    ▼
    [src/finance/indicators.py]
    │ (Tính toán chỉ báo vi cấu trúc: OBI Top 3, Intra-day Momentum, Foreign Flow)
    ▼
    [src/analytics/ranking.py]
    │ (Chuẩn hóa Percentile Ranking, Composite Multi-Factor Scoring 0-100, Phân tầng tín hiệu)
    ▼
    [src/app/main.py]
    │ (Streamlit Dashboard: Screener Realtime, Radar Chart, OBI Scatter, Order Depth)
    ▼
 NGƯỜI DÙNG (Nhà đầu tư / Giảng viên chấm thi UEL)
```

---

## ✅ CHECKLIST ĐỐI CHIẾU TIÊU CHÍ CHẤM

- [x] Nêu rõ vấn đề, người dùng, mục tiêu và giá trị tài chính.
- [x] NEO API là nguồn chính; có JWT, pagination, chuẩn hóa Pydantic, Token Bucket 5 req/s và SSI fallback.
- [x] Có OBI, thanh khoản, dòng tiền khối ngoại, động lượng, percentile ranking và cách diễn giải có trách nhiệm.
- [x] Mã nguồn phân lớp, xử lý lỗi, `.env.example`, `.gitignore` và pytest.
- [x] Dashboard có KPI, bảng, scatter, thanh khoản, gauge/radar, bộ lọc và trạng thái dữ liệu.
- [ ] Có demo video chưa chứa bí mật: `K244141706_NguyenHaYenVy_Demo.mp4`.
- [ ] Có kết quả live trong phiên được cấp quyền; unit test hiện đủ 9 ca nhưng chưa thay thế kiểm chứng API thực.
- [ ] Chưa được backtest ngoài mẫu; các ngưỡng/chất lượng không nên được tuyên bố là lợi nhuận dự báo.

---

## ⚖️ LIÊM CHÍNH HỌC THUẬT & TRÁCH NHIỆM NỘI DUNG

Sinh viên chịu trách nhiệm về mã nguồn, công thức, kết quả, trích dẫn và toàn bộ nội dung nộp. Tài liệu/thư viện bên ngoài được ghi nguồn theo thông lệ học thuật; dữ liệu thực không được thay bằng dữ liệu giả để làm đẹp kết quả.

Các fixture trong `tests/` chỉ dùng để kiểm chứng logic và được công bố là dữ liệu kiểm thử, không được xem là dữ liệu thị trường. Công cụ AI có thể hỗ trợ lập trình và biên tập; đầu ra AI không thay công thức tài chính, không được trình bày như sự thật đã kiểm chứng và hiện chưa được dùng để sinh kết luận thị trường.

---

## 🔒 BẢO MẬT, ĐỊA CHỈ IP WHITELIST & QUY TẮC DỮ LIỆU THẬT

1. **Cam kết 100% Dữ liệu Thật (Zero Mock):** Loại bỏ hoàn toàn mọi thuật toán sinh số ngẫu nhiên hoặc giả lập (`np.random`, `Math.random`). Tất cả giá trị giao dịch, bước giá sổ lệnh, khối lượng khớp và giao dịch khối ngoại đều là dữ liệu thực tế từ HOSE / VN30.
2. **Cơ chế Bảo mật IP Whitelist:**
   - Cấu hình IP được đặt trong biến môi trường `NEO_WHITELIST_IP`, không ghi cứng hoặc xuất bản cụ thể.
   - Khi trạm kết nối đáp ứng whitelist, hệ thống truy cập VPBankS NeoAPI bằng JWT Bearer (`POST /auth/token`).
   - Khi trạm không đáp ứng điều kiện whitelist, hệ thống có thể định tuyến sang cổng bổ sung **SSI FastConnect API** được người dùng ủy quyền.
3. **Tuân thủ Rate Limit:** Tích hợp bộ điều phối tốc độ `Token Bucket RateLimiter` giới hạn nghiêm ngặt **5 requests/giây**, bảo vệ hạ tầng NeoAPI theo quy định của VPBankS.
4. **An toàn bảo mật:** Thông tin tài khoản được tách biệt trong `.env` (mẫu tại `.env.example`), không commit thông tin nhạy cảm lên Git.

---

## 🔑 HƯỚNG DẪN CẤU HÌNH BIẾN MÔI TRƯỜNG (.env)

Tạo tệp `.env` tại thư mục gốc với các thông số cấu hình:
```bash
# 1. VPBankS NeoAPI Configuration
NEO_USERNAME=your_vpbanks_username
NEO_PASSWORD=your_vpbanks_password
NEO_ACCOUNT_NO=your_account_number
NEO_WHITELIST_IP=your_registered_private_ip
NEO_ENVIRONMENT=LIVE
NEO_API_BASE_URL=https://neoapi.vpbanks.com.vn/neo-api
NEO_AUTH_URL=https://external.vpbanks.com.vn/auth/token
NEO_DEVICE=neoapi-fintech-dashboard
NEO_DEVICE_TYPE=chrome
NEO_RATE_LIMIT_RPS=5.0

# 2. Supplementary Data Source: SSI FastConnect API
SSI_FASTCONNECT_URL=https://api.ssi.com.vn
SSI_IBOARD_URL=https://iboard-query.ssi.com.vn

# 3. Ứng dụng
APP_ENV=development
APP_PORT=8501
DEFAULT_UNIVERSE=VN30
```

---

## 📂 CẤU TRÚC THƯ MỤC NGUỒN
```
D:\K244141706_NguyenHaYenVy_NEOAPI_FinTech\
├── README.md                      # Hướng dẫn chi tiết & tổng quan hệ thống
├── requirements.txt               # Danh mục thư viện Python phụ thuộc
├── .env.example                   # Tệp mẫu cấu hình bảo mật
├── report/
│   └── K244141706_NguyenHaYenVy_BaoCao.md  # Báo cáo cuối kỳ 10 chương chuẩn mực
├── src/
│   ├── neo_api/
│   │   ├── config.py              # Pydantic Settings & Quản lý biến môi trường
│   │   ├── models.py              # Pydantic Data Models (Snapshot, OrderBook, ForeignTrade)
│   │   ├── client.py              # NeoAPI client, quản lý IP whitelist & failover
│   │   └── ssi_client.py          # SSI FastConnect API client (Kênh bổ sung 100% dữ liệu thật)
│   ├── finance/
│   │   └── indicators.py          # Bộ tính toán chỉ báo vi cấu trúc: OBI, Momentum, Foreign
│   ├── analytics/
│   │   └── ranking.py             # Động cơ Xếp hạng đa nhân tố, Composite Score & Phân tầng tín hiệu
│   └── app/
│       └── main.py                # Dashboard tương tác Streamlit (Bảng lọc, Radar, Scatter OBI)
└── tests/
    ├── test_neo_api.py            # Kiểm thử kết nối, IP Whitelisting, SSI Client & Parse dữ liệu
    └── test_finance_ranking.py    # Kiểm thử công thức chỉ báo tài chính & động cơ xếp hạng
```
