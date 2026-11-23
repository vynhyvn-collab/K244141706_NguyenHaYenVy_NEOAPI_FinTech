"""
Ứng dụng Bảng điều khiển Bộ lọc Cổ phiếu Thông minh (Smart Stock Screener).
Đồ án cá nhân: FinTech với VPBankS NEO API & SSI FastConnect API.
Sinh viên thực hiện: Nguyễn Hà Yến Vy - K244141706.
Khoa Tài chính - Ngân hàng, Trường Đại học Kinh tế - Luật (UEL).
"""
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.ranking import MultiFactorRankingEngine
from src.neo_api.client import NeoApiClient, NeoApiError
from src.neo_api.config import settings

# Múi giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

# Thiết lập cấu hình trang
st.set_page_config(
    page_title="NEO Screener | FinTech UEL",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện chuyên nghiệp
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 15px;
    }
    .status-box {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #E2E8F0;
        font-size: 13px;
    }
    .badge-top-buy {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-caution {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_neo_client():
    client = NeoApiClient()
    try:
        client.authenticate()
    except Exception:
        pass
    return client


def format_currency(val):
    if pd.isna(val) or val is None:
        return "N/A"
    abs_val = abs(val)
    if abs_val >= 1e9:
        return f"{val/1e9:+.2f} tỷ"
    elif abs_val >= 1e6:
        return f"{val/1e6:+.1f} tr"
    return f"{val:+,.0f}"


# --- KHỞI TẠO CLIENT & TẢI DỮ LIỆU ---
client = get_neo_client()

# --- SIDEBAR: Cấu hình & Bộ lọc ---
with st.sidebar:
    st.title("NEO API Screener")
    st.caption("Sinh viên: Nguyễn Hà Yến Vy (K244141706)")
    st.markdown("---")
    
    st.subheader("⚙️ Nguồn dữ liệu & Bảo mật")
    universe_choice = st.selectbox(
        "Phạm vi dữ liệu thị trường:",
        ["VN30 (30 Cổ phiếu Lớn nhất)", "ALL (Toàn bộ Sàn HOSE)"],
        index=0 if settings.DEFAULT_UNIVERSE == "VN30" else 1,
    )
    universe_key = "VN30" if "VN30" in universe_choice else "ALL"

    st.markdown("---")
    st.subheader("🔍 Bộ lọc chiến lược")
    filter_tier = st.multiselect(
        "Nhóm xếp hạng:",
        options=["Mạnh", "Tích cực", "Trung tính", "Yếu", "Thiếu dữ liệu"],
        default=["Mạnh", "Tích cực"]
    )
    
    min_score = st.slider("Điểm tổng hợp tối thiểu:", min_value=0, max_value=100, value=50, step=5)
    filter_market = st.multiselect("Sàn giao dịch:", ["HOSE", "HNX", "UPCOM", "FU", "BOND"])
    filter_normal_status = st.checkbox("Chỉ mã giao dịch bình thường (NORMAL)", value=True)
    filter_obi_positive = st.checkbox("Chỉ lấy mã Cầu mua áp đảo (OBI > 0)", value=False)
    filter_foreign_buy = st.checkbox("Chỉ lấy mã Khối ngoại mua ròng", value=False)
    
    st.markdown("---")
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# --- HEADER: Trạng thái & Tiêu đề ---
now_vn = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M:%S (UTC+7)")

try:
    with st.spinner("Đang tải dữ liệu thực tế từ thị trường chứng khoán Việt Nam..."):
        snapshots = client.get_market_universe(universe=universe_key)
    conn_status = client.get_connection_status()
except NeoApiError as exc:
    st.error(f"Không thể kết nối hoặc lấy dữ liệu thị trường: {exc}")
    st.stop()

col_title, col_status = st.columns([2.8, 1.2])
with col_title:
    st.markdown('<div class="main-header">HỆ THỐNG XẾP HẠNG & LỌC CỔ PHIẾU THÔNG MINH</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">'
        f'FinTech UEL | <b>100% Dữ liệu thực tế</b> | Cập nhật lúc: <b>{now_vn}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_status:
    provider_name = conn_status["active_provider"]
    is_neo = "VPBankS" in provider_name
    badge_icon = "🟢" if is_neo else "🔵"
    st.markdown(f"""
    <div class="status-box">
        <b>{badge_icon} Kênh dữ liệu:</b> {provider_name}<br>
        <b>🛡️ IP Whitelist:</b> <code>{conn_status['whitelisted_ip']}</code><br>
        <b>💻 IP Trạm kết nối:</b> <code>{conn_status['current_ip']}</code><br>
        <b>🔐 Xác thực VPBankS:</b> {'Đã cấp JWT' if conn_status['neo_authenticated'] else 'Chờ cấp'}
    </div>
    """, unsafe_allow_html=True)

# Thông báo điều phối bảo mật IP nếu có
if not conn_status["is_ip_matched"]:
    st.info(
        f"ℹ️ **Thông tin định tuyến:** Máy trạm đang phát tín hiệu từ IP `({conn_status['current_ip']})` khác với IP Whitelist đăng ký trên cổng VPBankS `({conn_status['whitelisted_ip']})`. "
        f"Hệ thống đã tự động kích hoạt **Kênh bổ sung SSI FastConnect API** (theo ủy quyền) để bảo đảm **100% dữ liệu giao dịch thật**, 0% mô phỏng.",
        icon="ℹ️"
    )

# --- TÍNH TOÁN XẾP HẠNG ĐA NHÂN TỐ ---
ranking_engine = MultiFactorRankingEngine()
ranked_results = ranking_engine.rank_universe(snapshots)

# Chuyển đổi thành DataFrame kết hợp
snapshot_dict = {s.symbol: s for s in snapshots}
data_rows = []
for r in ranked_results:
    snap = snapshot_dict[r.symbol]
    order_book = snap.order_book
    bid_volume = sum(level.volume for level in order_book.bids) if order_book else 0
    ask_volume = sum(level.volume for level in order_book.asks) if order_book else 0
    obi_value = (bid_volume - ask_volume) / (bid_volume + ask_volume) if bid_volume + ask_volume else float("nan")
    foreign_net = snap.foreign_trade.net_value if snap.foreign_trade else None
    
    data_rows.append({
        "Mã CP": r.symbol,
        "Sàn": snap.market_code or "HOSE",
        "Trạng thái": snap.trading_status or "NORMAL",
        "Giá (VNĐ)": snap.last_price,
        "Thay đổi (%)": snap.pct_change if snap.pct_change is not None else float("nan"),
        "Tổng KL khớp": snap.total_volume,
        "Tổng GTGD": snap.total_value,
        "OBI Sổ lệnh": obi_value,
        "Khối ngoại ròng": foreign_net if foreign_net is not None else float("nan"),
        "Điểm Tổng Hợp": r.composite_score if r.composite_score is not None else float("nan"),
        "Phân Hạng": r.ranking_tier,
        "Động lượng": r.momentum_score,
        "Thanh khoản": r.liquidity_score,
        "Khối ngoại": r.foreign_score,
        "Cung - Cầu (OBI)": r.order_book_imbalance_score,
        "Tín hiệu phân tích": r.signal_summary
    })

df_all = pd.DataFrame(data_rows)

# Áp dụng bộ lọc
df_filtered = df_all.copy()
if "Điểm Tổng Hợp" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Điểm Tổng Hợp"] >= min_score]
if filter_tier:
    df_filtered = df_filtered[df_filtered["Phân Hạng"].isin(filter_tier)]
if filter_market:
    df_filtered = df_filtered[df_filtered["Sàn"].isin(filter_market)]
if filter_normal_status:
    df_filtered = df_filtered[df_filtered["Trạng thái"] == "NORMAL"]
if filter_obi_positive:
    df_filtered = df_filtered[df_filtered["OBI Sổ lệnh"] > 0]
if filter_foreign_buy:
    df_filtered = df_filtered[df_filtered["Khối ngoại ròng"] > 0]

# --- METRIC CARDS TỔNG QUAN ---
st.markdown("### 📊 Tổng quan Độ rộng & Sức mạnh Thị trường")
m1, m2, m3, m4 = st.columns(4)
strong_count = (df_all["Phân Hạng"] == "Mạnh").sum()
advances = (df_all["Thay đổi (%)"] > 0).sum()
declines = (df_all["Thay đổi (%)"] < 0).sum()
foreign_net_values = df_all["Khối ngoại ròng"].dropna()
total_foreign_net = foreign_net_values.sum() if not foreign_net_values.empty else None

m1.metric("🏆 Số mã nhóm điểm Mạnh", f"{strong_count} / {len(df_all)}", delta="Phân vị hàng đầu")
m2.metric("⚖️ Độ rộng Giá", f"{advances} Tăng / {declines} Giảm", delta=f"{advances - declines} mã")
m3.metric("🌐 Tổng Mua/Bán Ròng Khối Ngoại", format_currency(total_foreign_net) if total_foreign_net is not None else "N/A", delta="Dòng vốn ngoại")
m4.metric("🎯 Mã đạt tiêu chí lọc", f"{len(df_filtered)} mã", delta=f"{len(df_filtered)/len(df_all):.0%}")

st.markdown("---")

# --- TABS GIAO DIỆN CHÍNH ---
tab_screener, tab_viz, tab_detail, tab_method = st.tabs([
    "📋 Bảng Lọc Thời Gian Thực",
    "📈 Trực Quan Hóa Vi Cấu Trúc",
    "🔬 Soi Kèo Chi Tiết Mã",
    "📚 Phương Pháp Luận & Miễn Trừ"
])

# TAB 1: BẢNG LỌC REALTIME
with tab_screener:
    st.subheader(f"Danh sách Cổ phiếu Xếp hạng theo Điểm Tổng Hợp ({len(df_filtered)} / {len(df_all)} mã)")
    
    def highlight_tier(val):
        if val == "Mạnh":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "Tích cực":
            return "background-color: #E0F2FE; color: #0369A1;"
        elif val == "Yếu":
            return "background-color: #FEE2E2; color: #991B1B;"
        return ""

    format_dict = {
        "Giá (VNĐ)": "{:,.0f}",
        "Thay đổi (%)": lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A",
        "Tổng KL khớp": "{:,.0f}",
        "Tổng GTGD": lambda x: f"{x/1e9:,.2f} tỷ" if pd.notna(x) and abs(x) >= 1e9 else f"{x/1e6:,.1f} tr" if pd.notna(x) else "N/A",
        "OBI Sổ lệnh": lambda x: f"{x:+.1%}" if pd.notna(x) else "N/A",
        "Khối ngoại ròng": lambda x: format_currency(x),
        "Điểm Tổng Hợp": lambda x: f"{x:.1f}" if pd.notna(x) else "N/A",
        "Động lượng": lambda x: f"{x:.1f}" if pd.notna(x) else "N/A",
        "Thanh khoản": lambda x: f"{x:.1f}" if pd.notna(x) else "N/A",
        "Khối ngoại": lambda x: f"{x:.1f}" if pd.notna(x) else "N/A",
        "Cung - Cầu (OBI)": lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
    }

    styled_df = df_filtered.style.map(highlight_tier, subset=["Phân Hạng"]).format(format_dict)
    st.dataframe(styled_df, use_container_width=True, height=480)
    st.caption("💡 Mẹo: Bấm vào tiêu đề cột để sắp xếp theo Điểm Tổng Hợp, OBI hoặc Khối ngoại.")

# TAB 2: TRỰC QUAN HÓA VI CẤU TRÚC
with tab_viz:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🎯 Tương quan Độ lệch Cung - Cầu (OBI) & Biến động Giá (%)")
        fig_scatter = px.scatter(
            df_all,
            x="OBI Sổ lệnh",
            y="Thay đổi (%)",
            size="Điểm Tổng Hợp",
            color="Phân Hạng",
            hover_name="Mã CP",
            hover_data=["Giá (VNĐ)", "Tổng GTGD"],
            color_discrete_map={
                "Mạnh": "#16A34A",
                "Tích cực": "#0284C7",
                "Trung tính": "#64748B",
                "Yếu": "#DC2626"
            },
            title="Độ lệch Sổ lệnh (OBI) vs Biến động Giá trong ngày"
        )
        fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_scatter.update_layout(height=420)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Scatter so sánh biến động giá phiên với OBI Top 3 từ các bước giá thực tế.")

    with col_chart2:
        st.markdown("#### 🌊 Thanh khoản phiên theo giá trị giao dịch")
        fig_bar = px.bar(
            df_all.sort_values(by="Tổng GTGD", ascending=False).head(15),
            x="Mã CP",
            y="Tổng GTGD",
            color="Điểm Tổng Hợp",
            color_continuous_scale="Viridis",
            title="Top 15 cổ phiếu theo giá trị giao dịch thực trong phiên"
        )
        fig_bar.update_layout(height=420)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Đường màu biểu thị điểm phân tích đa nhân tố; giá trị giao dịch trích xuất trực tiếp từ thị trường.")

# TAB 3: SOI KÈO CHI TIẾT MÃ
with tab_detail:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        symbol_list = df_all["Mã CP"].tolist()
        selected_symbol = st.selectbox("Chọn mã cổ phiếu phân tích sâu:", symbol_list)
    
    if selected_symbol and selected_symbol in snapshot_dict:
        selected_snap = snapshot_dict[selected_symbol]
        selected_row = df_all[df_all["Mã CP"] == selected_symbol].iloc[0]

        col_info, col_radar = st.columns([1, 1])

        with col_info:
            st.markdown(f"### 📌 Phân tích vi cấu trúc: **{selected_symbol}**")
            pct_display = f"{selected_snap.pct_change:+.2f}%" if selected_snap.pct_change is not None else "N/A"
            st.markdown(f"**Giá khớp gần nhất:** `{selected_snap.last_price:,.0f} VNĐ` ({pct_display})")
            st.markdown(f"**Nhóm điểm:** <span class='badge-top-buy'>{selected_row['Phân Hạng']}</span> (Điểm: **{selected_row['Điểm Tổng Hợp']} / 100**)", unsafe_allow_html=True)
            st.markdown(f"**Thuyết minh:** {selected_row['Tín hiệu phân tích']}")

            st.markdown("#### 📖 Chi tiết Sổ lệnh 3 Bước giá (Top 3 Bids & Asks)")
            ob = selected_snap.order_book
            bid_levels = ob.bids if ob else []
            ask_levels = ob.asks if ob else []

            col_bids, col_asks = st.columns(2)
            with col_bids:
                st.markdown("**BÊN MUA (BIDS)**")
                bid_df = pd.DataFrame([{"Giá": f"{b.price:,.0f}" if b.price is not None else (b.raw_price or "N/A"), "KL": f"{b.volume:,}"} for b in bid_levels])
                st.table(bid_df)
            with col_asks:
                st.markdown("**BÊN BÁN (ASKS)**")
                ask_df = pd.DataFrame([{"Giá": f"{a.price:,.0f}" if a.price is not None else (a.raw_price or "N/A"), "KL": f"{a.volume:,}"} for a in ask_levels])
                st.table(ask_df)

            tot_bid = sum(b.volume for b in bid_levels)
            tot_ask = sum(a.volume for a in ask_levels)
            if tot_bid + tot_ask > 0:
                bid_ratio = tot_bid / (tot_bid + tot_ask)
                st.progress(bid_ratio, text=f"Tỷ trọng KL đặt mua Top 3: {bid_ratio:.1%} | KL đặt bán: {1-bid_ratio:.1%}")
            else:
                st.info("Không có khối lượng sổ lệnh khả dụng cho mã này.")

        with col_radar:
            st.markdown("#### 🕸️ Radar các trụ cột vi cấu trúc")
            categories = ['Động lượng Giá', 'Khối ngoại', 'Sổ lệnh (OBI)']
            scores = [
                selected_row["Động lượng"],
                selected_row["Khối ngoại"],
                selected_row["Cung - Cầu (OBI)"]
            ]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=selected_symbol,
                line_color='#2563EB'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=False,
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

# TAB 4: PHƯƠNG PHÁP LUẬN & MIỄN TRỪ
with tab_method:
    st.markdown("""
    ### 📐 Kiến trúc Đa nguồn & Phương pháp Định lượng Vi cấu trúc

    Hệ thống được thiết kế theo mô hình **Dual-Engine Data Provider**:
    - **Cổng chính VPBankS NeoAPI:** Tuân thủ chuẩn JWT Bearer và IP Whitelist `14.187.239.157`.
    - **Cổng bổ sung SSI FastConnect API:** Tự động điều phối khi môi trường máy trạm nằm ngoài dải IP đã đăng ký, bảo đảm **100% dữ liệu thị trường thực tế**, không dùng số liệu mô phỏng.

    #### Các trụ cột định lượng vi cấu trúc:
    1. **Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI):**
       $$OBI = \\frac{\\sum_{i=1}^3 \\text{BidVol}_i - \\sum_{i=1}^3 \\text{AskVol}_i}{\\sum_{i=1}^3 \\text{BidVol}_i + \\sum_{i=1}^3 \\text{AskVol}_i} \\in [-1.0, 1.0]$$
       Phản ánh áp lực gom hàng hoặc phân phối ngắn hạn tại 3 bước giá khớp lệnh tốt nhất.
    
    2. **Thanh khoản & Giá trị Giao dịch:** Xếp hạng theo phân vị của `totalTradingValue` nhằm lọc các mã có thanh khoản thật và dòng tiền hoạt động mạnh.
    
    3. **Dòng tiền Nước ngoài (Foreign Flow Impact):**
       $$\\text{Foreign Impact} = \\frac{\\text{Foreign Net Value}}{\\text{Total Traded Value}}$$
       Đo lường mức độ tác động của khối ngoại tới tổng thanh khoản của cổ phiếu.

    4. **Động lượng phiên (Price Momentum):** Kết hợp tỷ lệ thay đổi giá trong phiên (`percentPriceChange`) và vị thế giá đóng cửa trong biên độ `lowPrice–highPrice`.
    
    5. **Điểm tổng hợp Đa nhân tố (Composite Multi-Factor Score):**
       $$\\text{Score} = w_{\\text{mom}} \\cdot S_{\\text{mom}} + w_{\\text{liq}} \\cdot S_{\\text{liq}} + w_{\\text{for}} \\cdot S_{\\text{for}} + w_{\\text{obi}} \\cdot S_{\\text{obi}}$$
       Trọng số chuẩn hóa phân vị từ 0 - 100 điểm, phân hạng thành 4 nhóm: **Mạnh (≥ 70)**, **Tích cực (55 - 70)**, **Trung tính (40 - 55)**, **Yếu (< 40)**.
    
    ---
    
    ### ⚠️ Khuyến cáo Rủi ro & Miễn trừ Trách nhiệm Học thuật
    - **Mục đích đồ án:** Đây là sản phẩm nghiên cứu ứng dụng công nghệ tài chính phục vụ học phần *Gói phần mềm ứng dụng cho tài chính 1* tại Trường Đại học Kinh tế - Luật (UEL).
    - **Không phải khuyến nghị đầu tư:** Mọi dữ liệu, phân tích, xếp hạng và tín hiệu trên bảng điều khiển chỉ mang tính chất tham khảo học thuật, không cấu thành bất kỳ lời chào mua/bán hay tư vấn đầu tư tài chính tiền thật nào.
    - **Giới hạn mô hình:** Dữ liệu sổ lệnh OBI phản ánh trạng thái tĩnh tại thời điểm truy vấn snapshot; không bảo đảm các lệnh đặt sẽ khớp toàn bộ trong diễn biến thị trường tiếp theo.
    """)
