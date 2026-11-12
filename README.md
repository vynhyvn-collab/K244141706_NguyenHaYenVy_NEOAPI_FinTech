# ĐỒ ÁN CUỐI KỲ: THỬ THÁCH ĐỔI MỚI CÔNG NGHỆ TÀI CHÍNH VỚI NEO API
**Môn học:** Gói phần mềm ứng dụng cho tài chính 1  
**Trường:** Đại học Kinh tế - Luật (UEL) - Khoa Tài chính - Ngân hàng  
**Sinh viên thực hiện:** Nguyễn Hà Yến Vy  
**Mã số sinh viên (MSSV):** K244141706  
**Mã lớp học phần:** 261BFF401101 / 261BFF401102  

---

## 1. Giới thiệu tổng quan đề tài
- **Tên đề tài:** Hệ thống Ra-đa Giám sát Vi cấu trúc Sổ lệnh & Dòng tiền Thị trường (Order Book Microstructure & Foreign Flow Radar).
- **Vấn đề giải quyết:** Hỗ trợ nhà đầu tư và chuyên viên phân tích theo dõi áp lực mua bán ngắn hạn thông qua mất cân bằng sổ lệnh (Order Book Imbalance - OBI) tại 3 bước giá, phát hiện bất thường thanh khoản và biến động dòng tiền ngoại theo thời gian thực từ dữ liệu chuẩn của NEO API (VPBankS).
- **Nguồn dữ liệu cốt lõi:** NEO API (VPBankS) - Hỗ trợ cả chế độ Live Streaming / REST và chế độ Mock / Replay dữ liệu mẫu nội ngày.

---

## 2. Cấu trúc thư mục dự án
```text
.
├── README.md                          # Hướng dẫn chi tiết sử dụng & kiểm chứng dự án
├── requirements.txt                   # Danh mục thư viện Python cần thiết
├── .env.example                       # Mẫu cấu hình biến môi trường (Bảo mật credentials)
├── src/
│   ├── neo_api/                       # Module kết nối, xác thực và thu thập dữ liệu NEO API
│   ├── data/                          # Chuẩn hóa múi giờ Asia/Ho_Chi_Minh, xử lý dữ liệu thiếu, lưu trữ
│   ├── finance/                       # Core Financial Logic: OBI, Spread, CVD, Liquidity Health Score
│   ├── analytics/                     # Thống kê định lượng: Z-score, phát hiện bất thường, phân phối
│   └── app/                           # Dashboard tương tác Streamlit
├── tests/                             # Bộ kiểm thử tự động (Unit Tests) với Pytest
├── data_sample/                       # Dữ liệu kiểm chứng mẫu (Ít nhất 5-10 phiên & tick data)
├── docs/                              # Tài liệu kỹ thuật, Data Dictionary, Sơ đồ kiến trúc
└── report/                            # Báo cáo cuối kỳ chi tiết (8-12 trang A4)
```

---

## 3. Hướng dẫn cài đặt và chạy ứng dụng

### Bước 1: Chuẩn bị môi trường
Yêu cầu Python 3.10 trở lên. Khuyến khích tạo môi trường ảo (virtualenv):
```bash
python -m venv venv
# Kích hoạt trên Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### Bước 2: Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình biến môi trường
Tạo file `.env` từ file mẫu:
```bash
copy .env.example .env
```
*(Mặc định `APP_ENV=MOCK` cho phép người chấm chạy thử nghiệm ngay lập tức với đầy đủ dữ liệu mẫu mà không cần kết nối API live).*

### Bước 4: Khởi chạy ứng dụng Dashboard
```bash
streamlit run src/app/main.py
```

### Bước 5: Chạy kiểm thử tự động
```bash
pytest tests/
```

---

## 4. Tuyên bố tuân thủ & Miễn trừ trách nhiệm
- Đồ án này chỉ phục vụ mục đích nghiên cứu học thuật trong khuôn khổ môn học tại UEL.
- Tuyệt đối không phát sinh giao dịch thật, không đặt lệnh mua/bán tiền thật trên thị trường.
- Tuân thủ nguyên tắc bảo mật: Không công khai thông tin xác thực cá nhân lên kho lưu trữ mã nguồn.
