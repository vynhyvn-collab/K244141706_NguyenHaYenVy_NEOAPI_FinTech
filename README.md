# ĐỒ ÁN CUỐI KỲ: BỘ LỌC CỔ PHIẾU THÔNG MINH (NEO API FINTECH)
### Smart Stock Screener & Multi-Factor Microstructure Ranking Engine

* **Trường:** Đại học Kinh tế - Luật (UEL) - Đại học Quốc gia TP.HCM  
* **Khoa:** Tài chính - Ngân hàng  
* **Học phần:** Gói phần mềm ứng dụng cho tài chính 1 (Mã lớp: 261BFF401101 / 261BFF401102)  
* **Sinh viên thực hiện:** Nguyễn Hà Yến Vy | **MSSV:** K244141706  
* **Nền tảng hạ tầng:** VPBankS NeoAPI & SSI FastConnect API v3 (100% Dữ liệu thực tế, 0% Mock)  
* **Nguyên tắc an toàn:** Tuyệt đối không lưu trữ khóa bí mật, mật khẩu hay địa chỉ IP riêng tư trên Git.

---

## 👨‍🏫 HƯỚNG DẪN DÀNH CHO GIẢNG VIÊN CHẤM ĐỒ ÁN (GRADING & EXECUTION GUIDE)

Để tạo thuận lợi tối đa cho Quý Thầy/Cô trong quá trình kiểm tra và đánh giá sản phẩm, dự án đã được thiết kế và kiểm thử sẵn sàng theo 3 phương thức vận hành:

### 🚀 Phương thức 1: Khởi chạy Dashboard trực tiếp (Khuyến nghị - Chạy ngay trong 1 dòng lệnh)
Giảng viên chỉ cần mở PowerShell (hoặc Terminal) tại thư mục dự án và chạy dòng lệnh:

```powershell
# Chạy với môi trường ảo có sẵn của dự án:
$env:PYTHONPATH="."; .\.venv\Scripts\streamlit.exe run src/app/main.py
```
*(Hoặc nếu chạy với môi trường Python chung của máy: `streamlit run src/app/main.py`)*

> **Điểm nổi bật:** Trình duyệt sẽ tự động mở tại `http://localhost:8501`. Giảng viên **không cần điền bất kỳ tài khoản hay mật khẩu nào**; hệ thống sẽ tự động kích hoạt kênh dữ liệu thị trường thực tế (HOSE / VN30) để hiển thị đầy đủ các tính năng phân tích vi cấu trúc, sổ lệnh Top 3 và khuyến nghị môi giới.

---

### 🧪 Phương thức 2: Chạy toàn bộ Bộ Kiểm thử Tự động (Unit Test Suite)
Để kiểm chứng tính đúng đắn của toàn bộ logic tài chính, công thức vi cấu trúc (OBI, Momentum, Foreign Flow) và cơ chế điều phối an toàn:

```powershell
# Chạy kiểm thử tự động với pytest:
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe -v
```

> **Kết quả kiểm chứng:** Toàn bộ **9/9 Unit Tests** đạt **100% Passed** trong ~1 giây, kiểm thử độc lập mà không cần kết nối mạng bên ngoài, chứng minh mã nguồn ổn định và tái lập kết quả dễ dàng.

---

### 🔑 Phương thức 3: Cấu hình Tài khoản Riêng (Tùy chọn dành cho Giảng viên / Chuyên viên)
Nếu Quý Thầy/Cô có tài khoản VPBankS NeoAPI hoặc SSI FastConnect API v3 riêng và muốn kiểm tra luồng xác thực:
1. Sao chép tệp mẫu `.env.example` thành `.env`:
   ```powershell
   cp .env.example .env
   ```
2. Điền thông tin tài khoản vào `.env` (xem hướng dẫn ở Mục 4 bên dưới).
3. Khởi chạy lại Streamlit; hệ thống sẽ tự động xác thực JWT Bearer chính thức với máy chủ.

---

## 🔒 CAM KẾT AN TOÀN VÀ QUYỀN RIÊNG TƯ (SECURITY & PRIVACY BY DESIGN)

Tuân thủ nghiêm ngặt quy định an toàn thông tin của đề tài:
1. **Không đưa dữ liệu nhạy cảm lên kho mã nguồn:** Tuyệt đối không hardcode tên đăng nhập, mật khẩu, API Key, API Secret, Private Key hay địa chỉ IP riêng tư trong mã nguồn, báo cáo hoặc tài liệu công khai.
2. **Cơ chế Quản lý Bí mật (.env & .gitignore):** 
   * Toàn bộ thông tin nhạy cảm được cô lập trong tệp `.env` cục bộ trên máy trạm của người dùng.
   * Tệp `.env` đã được đưa vào `.gitignore`, đảm bảo không bao giờ bị đẩy lên GitHub.
   * Dự án chỉ cung cấp tệp [.env.example](file:///.env.example) chứa các biến giả định (placeholders) để hướng dẫn cấu hình.
3. **An toàn Giao dịch (Read-Only Mode):** 
   * Sản phẩm chỉ khai thác quyền đọc dữ liệu thị trường (Market Data Read-Only), hoàn toàn không tích hợp tính năng đặt lệnh tiền thật, đảm bảo an toàn 100% cho tài sản của người dùng.
4. **Bảo vệ Hạ tầng (Rate Limiting 5 RPS):**
   * Tích hợp bộ điều phối `TokenBucket RateLimiter` giới hạn nghiêm ngặt 5 requests/giây, không bao giờ gây quá tải cho máy chủ của đối tác.

---

## 📖 GIỚI THIỆU BÀI TOÁN & GIÁ TRỊ THỰC TIỄN CHO NGƯỜI DÙNG

### 1. Vấn đề thực tế trong ngành chứng khoán:
* **Hạn chế của phân tích kỹ thuật truyền thống:** Các chỉ báo phổ biến (MA, RSI, MACD) chỉ tính trên giá đóng cửa quá khứ nên có độ trễ lớn. Khi phát tín hiệu Mua, giá thường đã tăng mạnh, khiến nhà đầu tư chịu rủi ro trượt giá và rủi ro chu kỳ T+2.5.
* **Quá tải bảng điện:** Hơn 1.600 mã cổ phiếu biến động từng giây, nhà đầu tư không thể theo dõi thủ công để tìm dấu vết dòng tiền lớn gom hàng.
* **Khoảng cách công nghệ:** Dữ liệu độ sâu sổ lệnh (Top 3 Bids/Asks) và Độ lệch Cung - Cầu (Order Book Imbalance - OBI) trước đây chỉ có trên các hệ thống đắt đỏ như Bloomberg/Refinitiv.

### 2. Định vị Người dùng mục tiêu:
* **Nhà đầu tư cá nhân chủ động (Active Trader):** Cần quét nhanh toàn thị trường dưới 1 giây, nhận diện các mã có bên Mua gom áp đảo kèm khối ngoại mua ròng, và có kế hoạch vào lệnh cụ thể (Vùng mua, Stop-loss, Target, R:R).
* **Môi giới chứng khoán & Chuyên viên tư vấn (Broker / Wealth Advisor):** Cần công cụ tạo ngay **Bản tin Khuyến nghị Khách hàng 1-Click (Broker Flash Note)** để sao chép gửi vào Zalo / Telegram cho khách hàng trong 5 giây.

---

## 🖥️ HƯỚNG DẪN ĐÁNH GIÁ 5 PHÂN KHU CHỨC NĂNG TRÊN DASHBOARD

Khi mở Dashboard tại `http://localhost:8501`, Giảng viên có thể tương tác trực tiếp với các phân khu:

1. **Thanh Thẻ An ninh & IP Trực quan:**
   * Hiển thị trạng thái xác thực, kênh dữ liệu hoạt động và dấu thời gian Việt Nam (`UTC+7`).
2. **Đồng hồ Đo Áp lực Toàn Thị trường (Market OBI Gauge):**
   * Đo lường tổng lực Cầu Mua vs Cung Bán tại Top 3 bước giá của toàn bộ rổ VN30, giúp nhận diện ngay thị trường phiên hôm nay đang nghiêng về **Phe Bò (Gom hàng)** hay **Phe Gấu (Đè bán)**.
3. **Tab 1 - Bảng Lọc Realtime & Ma trận Chiến lược Thực chiến:**
   * Tự động gắn nhãn chiến lược cho từng mã: 🚀 *Mua Bứt Phá*, 🛡️ *Tích Lũy Gom*, ⚪ *Quan Sát*, ⚠️ *Cảnh Báo Bán*.
   * Đề xuất tỷ trọng giải ngân cụ thể (% NAV: 15%–20%, 10%–15%, hoặc 0% Đứng ngoài).
4. **Tab 2 - Trực quan hóa Vi cấu trúc (Visual Analytics):**
   * Biểu đồ phân tán Scatter OBI vs Biến động giá $\%\Delta P$ giúp bóc tách mối tương quan giữa áp lực đặt lệnh và biến động giá.
   * Biểu đồ thanh ngang phân bổ giá trị giao dịch thực tế Top 15 cổ phiếu.
5. **Tab 3 - Soi kèo Sổ lệnh & Kế hoạch Quản trị Rủi ro:**
   * Bảng chi tiết 3 bước giá Mua/Bán và thanh tiến trình đo lường tỷ lệ gom hàng.
   * Khung kế hoạch vào lệnh: Tự động tính toán **Vùng mua an toàn**, **Mục tiêu lợi nhuận (Target)**, **Ngưỡng cắt lỗ kỷ luật (Stop-Loss)** và tỷ lệ **Lợi nhuận/Rủi ro ($R:R$)**.
   * Biểu đồ Radar 3 trục sức mạnh vi cấu trúc.
6. **Tab 4 - Bộ Công cụ Môi giới Tạo Bản tin Tư vấn 1-Click (Broker Toolkit):**
   * Môi giới chọn mã cổ phiếu, hệ thống tự động sinh bản tin khuyến nghị chuyên nghiệp chuẩn Công ty Chứng khoán, sẵn sàng bấm `Ctrl + C` để gửi khách hàng.
7. **Tab 5 - Phương pháp luận Định lượng & Miễn trừ Học thuật:**
   * Minh bạch toàn bộ công thức toán học (Cartea & Jaimungal, 2014) và tuyên bố trách nhiệm học thuật theo chuẩn đề thi UEL.

---

## 🏗️ KIẾN TRÚC DỮ LIỆU KÉP (DUAL-ENGINE ARCHITECTURE)

```
           ┌────────────────────────────────────────────────────────┐
           │     KIẾN TRÚC NGUỒN DỮ LIỆU KÉP (DUAL-ENGINE)          │
           │                                                        │
           │   [Cổng Chính]                    [Cổng Bổ Sung]       │
           │   VPBankS NeoAPI                  SSI FastConnect v3   │
           │   (Xác thực JWT Bearer)           (Ủy quyền tài khoản) │
           └──────────┬─────────────────────────────────┬───────────┘
                      │                                 │
                      ▼                                 ▼
         [src/neo_api/client.py & src/neo_api/ssi_client.py]
         │ (Tự động phát hiện IP, điều phối luồng dữ liệu 100% Thật)
         ▼
    [Chuẩn hóa dữ liệu: Pydantic Data Models]
    │ (StockSnapshot, StockOrderBook, PriceLevel, ForeignTrade)
    ▼
    [src/finance/indicators.py]
    │ (Tính toán vi cấu trúc: OBI Top 3, Intra-day Momentum, Foreign Impact)
    ▼
    [src/analytics/ranking.py]
    │ (Chuẩn hóa Percentile Ranking 0-100, Composite Multi-Factor Scoring)
    ▼
    [src/app/main.py]
    │ (Streamlit Dashboard: Screener Realtime, Radar, Scatter OBI, Broker Toolkit)
    ▼
 NGƯỜI DÙNG (Nhà đầu tư cá nhân / Chuyên viên Môi giới / Giảng viên UEL)
```

---

## 🔑 CẤU TRÚC MẪU CỦA TỆP BIẾN MÔI TRƯỜNG (.env.example)

Quý Thầy/Cô hoặc người dùng muốn cấu hình tài khoản thực chỉ cần tham khảo [.env.example](file:///.env.example):
```bash
# 1. Cấu hình VPBankS NeoAPI (Chỉ lưu trong .env cục bộ, không commit lên Git)
NEO_USERNAME=your_vpbanks_username
NEO_PASSWORD=your_vpbanks_password
NEO_ACCOUNT_NO=your_account_number
NEO_WHITELIST_IP=your_registered_ip
NEO_ENVIRONMENT=LIVE
NEO_API_BASE_URL=https://neoapi.vpbanks.com.vn/neo-api
NEO_AUTH_URL=https://external.vpbanks.com.vn/auth/token
NEO_DEVICE=neoapi-fintech-dashboard
NEO_DEVICE_TYPE=chrome
NEO_REQUEST_TIMEOUT=15
NEO_RATE_LIMIT_RPS=5.0

# 2. Cấu hình Kênh bổ sung SSI FastConnect API v3
SSI_FASTCONNECT_URL=https://api.ssi.com.vn
SSI_IBOARD_URL=https://iboard-query.ssi.com.vn
SSI_API_KEY=your_ssi_api_key
SSI_API_SECRET=your_ssi_api_secret
SSI_PRIVATE_KEY=your_ssi_rsa_private_key

# 3. Cấu hình Ứng dụng
APP_ENV=development
APP_PORT=8501
DEFAULT_UNIVERSE=VN30
```

---

## 📂 CẤU TRÚC THƯ MỤC NGUỒN
```
D:\K244141706_NguyenHaYenVy_NEOAPI_FinTech\
├── README.md                      # Hướng dẫn chi tiết & tài liệu dành cho giảng viên chấm
├── requirements.txt               # Danh mục thư viện Python phụ thuộc
├── .env.example                   # Tệp mẫu cấu hình bảo mật (chỉ chứa placeholder)
├── .gitignore                     # Bảo vệ tệp .env và bí mật không bị đẩy lên Git
├── report/
│   └── K244141706_NguyenHaYenVy_BaoCao.md  # Báo cáo cuối kỳ 10 chương chuẩn mực đề thi
├── src/
│   ├── neo_api/
│   │   ├── config.py              # Pydantic Settings & Quản lý biến môi trường an toàn
│   │   ├── models.py              # Pydantic Data Models (Snapshot, OrderBook, ForeignTrade)
│   │   ├── client.py              # NeoAPI client, quản lý IP whitelist & failover
│   │   └── ssi_client.py          # SSI FastConnect v3 client (Kênh bổ sung 100% dữ liệu thật)
│   ├── finance/
│   │   └── indicators.py          # Bộ tính toán chỉ báo vi cấu trúc: OBI, Momentum, Foreign
│   ├── analytics/
│   │   └── ranking.py             # Động cơ Xếp hạng đa nhân tố, Composite Score & Phân tầng tín hiệu
│   └── app/
│       └── main.py                # Dashboard tương tác Streamlit (5 Tab chức năng thực chiến)
└── tests/
    ├── test_neo_api.py            # Kiểm thử xác thực JWT, IP whitelist, SSI Client & Parse dữ liệu
    └── test_finance_ranking.py    # Kiểm thử công thức chỉ báo tài chính & động cơ xếp hạng
```
