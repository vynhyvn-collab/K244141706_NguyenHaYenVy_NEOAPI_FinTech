# ĐỒ ÁN CUỐI KỲ: BỘ LỌC CỔ PHIẾU THÔNG MINH (NEO API FINTECH)
### Smart Stock Screener & Multi-Factor Microstructure Ranking Engine

* **Trường:** Đại học Kinh tế - Luật (UEL) - Đại học Quốc gia TP.HCM  
* **Khoa:** Tài chính - Ngân hàng  
* **Học phần:** Gói phần mềm ứng dụng cho tài chính 1 (Mã lớp: 261BFF401101 / 261BFF401102)  
* **Sinh viên thực hiện:** Nguyễn Hà Yến Vy | **MSSV:** K244141706  
* **Nền tảng hạ tầng:** VPBankS NeoAPI & SSI FastConnect API v3 (100% Dữ liệu thực tế, Zero Mock)  
* **Nguyên tắc an toàn:** Tuyệt đối không lưu trữ khóa bí mật, mật khẩu hay địa chỉ IP riêng tư trên Git.

---

## 👨‍🏫 HƯỚNG DẪN DÀNH CHO GIẢNG VIÊN VÀ NHÀ ĐẦU TƯ: CẤU HÌNH TÀI KHOẢN RIÊNG QUA TỆP `.env` (TỪ `.env.example`)

Để bảo đảm tính bảo mật tối đa và trao toàn quyền kiểm soát tham số môi trường cho Quý Thầy/Cô và Nhà đầu tư khi thử nghiệm hệ thống bằng tài khoản cá nhân, dự án vận hành thông qua cơ chế cấu hình biến môi trường chuẩn quốc tế bằng tệp `.env`.

### 📋 Quy trình 5 Bước Khởi chạy Dự án:

#### Bước 1: Sao chép tệp mẫu `.env.example` thành `.env`
Mở PowerShell (hoặc Terminal) tại thư mục gốc của dự án và chạy lệnh:

```powershell
# Trên Windows PowerShell:
Copy-Item .env.example .env

# Hoặc trên Command Prompt (cmd) / Bash:
# copy .env.example .env     (cmd)
# cp .env.example .env       (bash)
```

#### Bước 2: Điền thông tin tài khoản cá nhân vào tệp `.env`
Mở tệp `.env` vừa tạo bằng trình soạn thảo văn bản (Notepad, VS Code,...) và cấu hình các trường thông tin:

```bash
# ------------------------------------------------------------------------------
# 1. Cấu hình Tài khoản VPBankS NeoAPI (Dựa trên tài liệu đặc tả 158 trang)
# ------------------------------------------------------------------------------
NEO_USERNAME="your_vpbanks_username"          # Tên đăng nhập VPBankS NeoAPI
NEO_PASSWORD="your_vpbanks_password"          # Mật khẩu đăng nhập VPBankS NeoAPI
NEO_ACCOUNT_NO="your_vpbanks_account_no"      # Số tài khoản giao dịch
NEO_WHITELIST_IP="your_whitelisted_ip"        # IP tĩnh đã đăng ký với VPBankS (nếu có)
NEO_ENVIRONMENT=LIVE
NEO_API_BASE_URL=https://neoapi.vpbanks.com.vn/neo-api
NEO_AUTH_URL=https://external.vpbanks.com.vn/auth/token
NEO_DEVICE=neoapi-fintech-dashboard
NEO_DEVICE_TYPE=chrome
NEO_REQUEST_TIMEOUT=15
NEO_RATE_LIMIT_RPS=5.0

# ------------------------------------------------------------------------------
# 2. Cấu hình Kênh Bổ sung SSI FastConnect API v3 (Đặc tả Developer Portal 457 trang)
# ------------------------------------------------------------------------------
SSI_FASTCONNECT_URL=https://api.ssi.com.vn
SSI_IBOARD_URL=https://iboard-query.ssi.com.vn
SSI_API_KEY="your_ssi_api_key"                # Consumer API Key từ SSI Developer Portal
SSI_API_SECRET="your_ssi_api_secret"          # Consumer API Secret từ SSI Developer Portal
SSI_PRIVATE_KEY=""                            # RSA Private Key (đặt trong dấu ngoặc kép nếu có)

# ------------------------------------------------------------------------------
# 3. Cấu hình Tham số Khởi động Ứng dụng
# ------------------------------------------------------------------------------
APP_ENV=development
APP_PORT=8501
DATA_CACHE_DIR=./data_sample
DEFAULT_UNIVERSE=ALL                          # Mặc định lấy 100% toàn bộ thị trường
```

> **Ghi chú về nguồn cấp:**
> * Hệ thống hỗ trợ cơ chế điều phối thông minh: Tự động kết nối **VPBankS NeoAPI** qua JWT Bearer.
> * Nếu môi trường mạng cục bộ chưa kịp đăng ký IP Whitelist với VPBankS, hệ thống tự động định tuyến sang cổng bổ sung **SSI FastConnect API v3** để đảm bảo luôn hiển thị **100% dữ liệu thị trường thực tế**, không gián đoạn trải nghiệm của Giảng viên.

#### Bước 3: Cài đặt thư viện phụ thuộc (nếu chưa có môi trường ảo)
```powershell
pip install -r requirements.txt
```

#### Bước 4: Khởi chạy Bảng điều khiển Định lượng (Streamlit Dashboard)
```powershell
# Chạy với môi trường ảo của dự án:
$env:PYTHONPATH="."; .\.venv\Scripts\streamlit.exe run src/app/main.py

# Hoặc nếu chạy với Python hệ thống:
streamlit run src/app/main.py
```
Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

#### Bước 5: Chạy Bộ Kiểm thử Tự động (Unit Test Suite)
Để kiểm tra tính toàn vẹn của logic vi cấu trúc (OBI, Momentum, Foreign Flow) và khả năng xử lý dữ liệu:
```powershell
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe -v
```
> Toàn bộ các kiểm thử đơn vị sẽ hoàn thành trong ~1 giây với kết quả **100% PASSED** mà không cần phụ thuộc vào mạng ngoài.

---

## 🌐 KHẢ NĂNG XỬ LÝ 100% DỮ LIỆU THỰC TẾ TOÀN BỘ CÁC MÃ TRÊN THỊ TRƯỜNG

Hệ thống được lập trình dựa trên 2 bộ tài liệu kỹ thuật chính thức:
1. **VPBankS NEO API Specification (158 trang):**
   * Endpoint `GET /stock/stockDetail?marketCode=ALL` hỗ trợ phân trang (`pageNo`, `pageSize`, `totalPages`) tải toàn bộ dữ liệu thị trường.
   * Endpoint `GET /stock/stockDetailByIndex?indexCode=VN30` tải rổ chỉ số VN30.
2. **SSI FastConnect API v3 & iBoard Query Specification (457 trang):**
   * Sàn HOSE (`/stock/exchange/hose`): ~414 mã cổ phiếu niêm yết.
   * Sàn HNX (`/stock/exchange/hnx`): ~299 mã cổ phiếu niêm yết.
   * Sàn UPCOM (`/stock/exchange/upcom`): ~807 mã cổ phiếu đăng ký giao dịch.
   * Rổ VN30 (`/stock/group/VN30`): 30 cổ phiếu đầu ngành có tính thanh khoản cao nhất.

Khi người dùng chọn tùy chọn `ALL (100% Toàn bộ Thị trường: HOSE, HNX, UPCOM)`, hệ thống sẽ quét và hợp nhất hơn **1.520+ mã cổ phiếu**, mang lại bức tranh định lượng hoàn chỉnh cho toàn thị trường chứng khoán Việt Nam mà không dùng bất kỳ dữ liệu giả lập (Zero Mock Data).

---

## 🖥️ THIẾT KẾ GIAO DIỆN HỢP NHẤT 1 TAB DUY NHẤT (ALL-IN-ONE DASHBOARD)

Nhằm tối ưu hóa luồng thao tác của Giảng viên và Nhà đầu tư, giao diện ứng dụng được cấu trúc thành **1 Tab Duy Nhất**:  
`📊 BẢNG ĐIỀU KHIỂN ĐỊNH LƯỢNG TOÀN THỊ TRƯỜNG & HỖ TRỢ RA QUYẾT ĐỊNH`

Toàn bộ 5 phân khu chức năng được trình bày liên tục, trực quan theo thứ tự phân tích tài chính logic:

```
┌────────────────────────────────────────────────────────────────────────┐
│  THANH TRẠNG THÁI HỆ THỐNG: Kênh dữ liệu thực tế, Whitelist IP, Giờ VN │
├────────────────────────────────────────────────────────────────────────┤
│  TỔNG QUAN ÁP LỰC: Đồng hồ Market OBI Gauge & 6 Thẻ Metric Thanh khoản │
├────────────────────────────────────────────────────────────────────────┤
│  [TAB DUY NHẤT: BẢNG ĐIỀU KHIỂN ĐỊNH LƯỢNG TOÀN DIỆN & HỖ TRỢ RA QUYẾT ĐỊNH]
│                                                                        │
│  📋 PHẦN 1: BẢNG LỌC CỔ PHIẾU ĐỊNH LƯỢNG & CHIẾN LƯỢC THỰC CHIẾN       │
│     • Bảng lọc realtime đa nhân tố (Giá, %ΔP, OBI, Khối ngoại, Điểm)   │
│     • Gắn nhãn chiến lược tự động: 🚀 Mua Bứt Phá, 🛡️ Tích Lũy Gom,    │
│       ⚪ Quan Sát, ⚠️ Cảnh Báo Bán                                     │
│     • Lọc động theo sàn (HOSE, HNX, UPCOM) và điểm số tối thiểu        │
│                                                                        │
│  📈 PHẦN 2: TRỰC QUAN HÓA VI CẤU TRÚC TOÀN THỊ TRƯỜNG                 │
│     • Scatter Plot: Mối quan hệ giữa Độ lệch Sổ lệnh (OBI) & %ΔP Giá   │
│     • Bar Chart: Phân bổ thanh khoản tiền thật Top 15 cổ phiếu lớn nhất│
│                                                                        │
│  🔬 PHẦN 3: SOI KÈO SỔ LỆNH CHI TIẾT & KHUNG QUẢN TRỊ RỦI RO           │
│     • Bóc tách độ sâu sổ lệnh Top 3 Bước giá Bids / Asks               │
│     • Thanh tiến trình đo tỷ lệ Gom Mua vs Đè Bán                      │
│     • Khung mô phỏng tham chiếu: Vùng mua, Target, Stop-Loss, Tỷ lệ R:R│
│     • Radar Chart 3 trục sức mạnh: Động lượng - Khối ngoại - OBI       │
│                                                                        │
│  📢 PHẦN 4: BẢN TIN PHÂN TÍCH HỌC THUẬT (BROKER FLASH NOTE)            │
│     • Trình tạo tự động báo cáo phân tích vi cấu trúc 1-click          │
│     • Sẵn sàng sao chép gửi khách hàng/nhà đầu tư                      │
│                                                                        │
│  📚 PHẦN 5: PHƯƠNG PHÁP LUẬN ĐỊNH LƯỢNG & MIỄN TRỪ TRÁCH NHIỆM         │
│     • Minh bạch công thức toán học OBI, Momentum, Liquidity, Foreign   │
│     • Tuyên bố miễn trừ rủi ro học thuật chuẩn mực UEL                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 CAM KẾT BẢO MẬT VÀ QUYỀN RIÊNG TƯ (SECURITY BY DESIGN)

1. **Không rò rỉ khóa bí mật:** Toàn bộ khóa truy cập và thông tin nhạy cảm được quản lý độc quyền qua biến môi trường cục bộ `.env`.
2. **Loại trừ khỏi Git:** Tệp `.env` đã được đưa vào `.gitignore`, tuyệt đối không bao giờ xuất hiện trên GitHub hay kho lưu trữ mã nguồn mở.
3. **Chế độ Chỉ Đọc (Read-Only Safety):** Hệ thống chỉ thực hiện các lệnh truy vấn dữ liệu thị trường (Market Data), không có mã lệnh gửi/hủy lệnh tiền thật, triệt tiêu mọi rủi ro tài chính.
4. **Bảo vệ Hạ tầng API (Rate Limiting 5 RPS):** Tích hợp thuật toán `TokenBucket` kiểm soát tốc độ gọi API tối đa 5 yêu cầu/giây, tuân thủ đạo đức sử dụng hạ tầng của công ty chứng khoán.

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

```
D:\K244141706_NguyenHaYenVy_NEOAPI_FinTech\
├── README.md                      # Tài liệu hướng dẫn chi tiết dành cho Giảng viên & Nhà đầu tư
├── requirements.txt               # Danh mục thư viện Python phụ thuộc
├── .env.example                   # Tệp mẫu cấu hình biến môi trường an toàn
├── .gitignore                     # Bảo vệ tệp .env và bí mật cục bộ
├── report/
│   └── K244141706_NguyenHaYenVy_BaoCao.md  # Báo cáo học thuật cuối kỳ 10 chương
├── src/
│   ├── neo_api/
│   │   ├── config.py              # Pydantic Settings & nạp biến môi trường an toàn
│   │   ├── models.py              # Pydantic Data Models (Snapshot, OrderBook, ForeignTrade)
│   │   ├── client.py              # NeoAPI client, quản lý kết nối & điều phối thông minh
│   │   └── ssi_client.py          # SSI FastConnect v3 client (100% dữ liệu thật HOSE, HNX, UPCOM)
│   ├── finance/
│   │   └── indicators.py          # Bộ chỉ báo vi cấu trúc: OBI Top 3, Intra-day Momentum, Foreign Impact
│   ├── analytics/
│   │   └── ranking.py             # Động cơ Xếp hạng đa nhân tố & phân loại chiến lược thực chiến
│   └── app/
│       └── main.py                # Dashboard Streamlit Hợp nhất 1 Tab duy nhất (All-in-One)
└── tests/
    ├── test_neo_api.py            # Kiểm thử xác thực JWT, IP whitelist, SSI Client & Parse dữ liệu
    └── test_finance_ranking.py    # Kiểm thử công thức chỉ báo tài chính & động cơ xếp hạng
```
