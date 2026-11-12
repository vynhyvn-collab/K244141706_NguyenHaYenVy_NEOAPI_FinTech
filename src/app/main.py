"""
Ứng dụng Bảng điều khiển Bộ lọc Cổ phiếu Thông minh (Smart Stock Screener).
Đồ án cá nhân: FinTech với VPBankS NEO API.
Sinh viên thực hiện: Nguyễn Hà Yến Vy - K244141706.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

from src.neo_api.client import NeoApiClient
from src.neo_api.config import settings
from src.analytics.ranking import MultiFactorRankingEngine

# Múi giờ Việt Nam
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
        font-size: 28px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #3B82F6;
    }
    .badge-top-buy {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-caution {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_neo_client():
    client = NeoApiClient()
    client.authenticate()
    return client


def format_currency(val):
    if abs(val) >= 1e9:
        return f"{val/1e9:.2f} tỷ"
    elif abs(val) >= 1e6:
        return f"{val/1e6:.1f} tr"
    return f"{val:,.0f}"


# --- SIDEBAR: Cấu hình & Bộ lọc ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3310/3310624.png", width=60)
    st.title("NEO API Screener")
    st.caption("Sinh viên: Nguyễn Hà Yến Vy (K244141706)")
    st.markdown("---")
    
    st.subheader("⚙️ Nguồn dữ liệu & Cấu hình")
    env_mode = st.radio(
        "Chế độ dữ liệu:",
        options=["MOCK (Mô phỏng chuẩn)", "LIVE (NEO API Thật)"],
        index=0 if settings.NEO_ENVIRONMENT == "MOCK" else 1
    )
    
    universe = st.selectbox("Rổ cổ phiếu:", ["VN30", "Top 10 Thanh khoản"], index=0)
    
    st.markdown("---")
    st.subheader("🔍 Bộ lọc chiến lược")
    filter_tier = st.multiselect(
        "Nhóm xếp hạng:",
        options=["Top Buy", "Accumulation", "Neutral", "Caution"],
        default=["Top Buy", "Accumulation"]
    )
    
    min_score = st.slider("Điểm tổng hợp tối thiểu:", min_value=0, max_value=100, value=50, step=5)
    filter_obi_positive = st.checkbox("Chỉ lấy mã Cầu mua áp đảo (OBI > 0)", value=False)
    filter_vol_spike = st.checkbox("Chỉ lấy mã Đột biến Vol (RelVol > 1.2x)", value=False)
    filter_foreign_buy = st.checkbox("Chỉ lấy mã Khối ngoại mua ròng", value=False)
    
    st.markdown("---")
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# --- HEADER: Trạng thái & Tiêu đề ---
now_vn = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M:%S (UTC+7)")
client = get_neo_client()

col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-header">HỆ THỐNG XẾP HẠNG & LỌC CỔ PHIẾU THÔNG MINH</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Mô hình định lượng đa nhân tố vi cấu trúc sổ lệnh (OBI) trên nền tảng VPBankS NEO API | Cập nhật: <b>{now_vn}</b></div>', unsafe_allow_html=True)

with col_status:
    status_color = "🟢" if client.jwt_token else "🔴"
    st.info(f"{status_color} **Trạng thái NEO API:** Kết nối tốt\n\n**Môi trường:** {env_mode.split()[0]}")

# --- TẢI DỮ LIỆU & TÍNH TOÁN ---
with st.spinner("Đang tải dữ liệu vi cấu trúc sổ lệnh từ NEO API..."):
    snapshots = client.get_market_universe(universe=universe)
    ranking_engine = MultiFactorRankingEngine()
    ranked_results = ranking_engine.rank_universe(snapshots)

# Chuyển đổi thành DataFrame kết hợp
snapshot_dict = {s.symbol: s for s in snapshots}
data_rows = []
for r in ranked_results:
    snap = snapshot_dict[r.symbol]
    data_rows.append({
        "Mã CP": r.symbol,
        "Giá (VNĐ)": snap.last_price,
        "Thay đổi (%)": snap.pct_change,
        "Tổng GTGD": snap.total_value,
        "RelVol (x TB20)": snap.total_volume / snap.avg_volume_20d if snap.avg_volume_20d > 0 else 1.0,
        "OBI Sổ lệnh": (sum(b.volume for b in snap.order_book.bids) - sum(a.volume for a in snap.order_book.asks)) / 
                        max(1, sum(b.volume for b in snap.order_book.bids) + sum(a.volume for a in snap.order_book.asks)),
        "Khối ngoại ròng": snap.foreign_trade.net_value if snap.foreign_trade else 0.0,
        "Điểm Tổng Hợp": r.composite_score,
        "Phân Hạng": r.ranking_tier,
        "Động lượng": r.momentum_score,
        "Thanh khoản": r.liquidity_score,
        "Khối ngoại": r.foreign_score,
        "Cung - Cầu (OBI)": r.order_book_imbalance_score,
        "Tín hiệu phân tích": r.signal_summary
    })

df_all = pd.DataFrame(data_rows)

# Áp dụng bộ lọc
df_filtered = df_all[df_all["Điểm Tổng Hợp"] >= min_score]
if filter_tier:
    df_filtered = df_filtered[df_filtered["Phân Hạng"].isin(filter_tier)]
if filter_obi_positive:
    df_filtered = df_filtered[df_filtered["OBI Sổ lệnh"] > 0]
if filter_vol_spike:
    df_filtered = df_filtered[df_filtered["RelVol (x TB20)"] >= 1.2]
if filter_foreign_buy:
    df_filtered = df_filtered[df_filtered["Khối ngoại ròng"] > 0]

# --- METRIC CARDS TỔNG QUAN ---
st.markdown("### 📊 Tổng quan Độ rộng & Sức mạnh Thị trường")
m1, m2, m3, m4 = st.columns(4)
top_buy_count = (df_all["Phân Hạng"] == "Top Buy").sum()
advances = (df_all["Thay đổi (%)"] > 0).sum()
declines = (df_all["Thay đổi (%)"] < 0).sum()
total_foreign_net = df_all["Khối ngoại ròng"].sum()

m1.metric("🏆 Số mã đạt 'Top Buy'", f"{top_buy_count} / {len(df_all)}", delta="Tín hiệu gom mạnh")
m2.metric("⚖️ Độ rộng Giá", f"{advances} Tăng / {declines} Giảm", delta=f"{advances - declines} mã")
m3.metric("🌐 Tổng Mua/Bán Ròng Khối Ngoại", format_currency(total_foreign_net), delta="Dòng vốn ngoại")
m4.metric("🎯 Mã đạt tiêu chí lọc", f"{len(df_filtered)} mã", delta=f"{len(df_filtered)/len(df_all):.0%}")

st.markdown("---")

# --- TABS GIAO DIỆN CHÍNH ---
tab_screener, tab_viz, tab_detail, tab_method = st.tabs([
    "📋 Bảng Lọc Realtime",
    "📈 Trực Quan Hóa Vi Cấu Trúc",
    "🔬 Soi Kèo Chi Tiết Mã",
    "📚 Phương Pháp Luận & Miễn Trừ"
])

# TAB 1: BẢNG LỌC REALTIME
with tab_screener:
    st.subheader("Danh sách Cổ phiếu Xếp hạng theo Điểm Tổng Hợp (Composite Score)")
    
    def highlight_tier(val):
        if val == "Top Buy":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "Accumulation":
            return "background-color: #E0F2FE; color: #0369A1;"
        elif val == "Caution":
            return "background-color: #FEE2E2; color: #991B1B;"
        return ""

    format_dict = {
        "Giá (VNĐ)": "{:,.0f}",
        "Thay đổi (%)": "{:+.2f}%",
        "Tổng GTGD": lambda x: format_currency(x),
        "RelVol (x TB20)": "{:.2f}x",
        "OBI Sổ lệnh": "{:+.1%}",
        "Khối ngoại ròng": lambda x: format_currency(x),
        "Điểm Tổng Hợp": "{:.1f}",
        "Động lượng": "{:.1f}",
        "Thanh khoản": "{:.1f}",
        "Khối ngoại": "{:.1f}",
        "Cung - Cầu (OBI)": "{:.1f}"
    }

    # Pandas 2.1+ / 3.x sử dụng map thay vì applymap
    styled_df = df_filtered.style.map(highlight_tier, subset=["Phân Hạng"])\
                                 .format(format_dict)
    
    st.dataframe(styled_df, use_container_width=True, height=450)
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
            hover_data=["Giá (VNĐ)", "RelVol (x TB20)"],
            color_discrete_map={
                "Top Buy": "#16A34A",
                "Accumulation": "#0284C7",
                "Neutral": "#64748B",
                "Caution": "#DC2626"
            },
            title="Độ lệch Sổ lệnh (OBI) vs Biến động Giá trong ngày"
        )
        fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_scatter.update_layout(height=420)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Góc phần tư trên cùng bên phải: Cổ phiếu tăng giá kèm lực Cầu gom sổ lệnh áp đảo (Tín hiệu bền vững).")

    with col_chart2:
        st.markdown("#### 🌊 Bản đồ Dòng tiền & Đột biến Khối lượng (Relative Volume)")
        fig_bar = px.bar(
            df_all.sort_values(by="RelVol (x TB20)", ascending=False).head(15),
            x="Mã CP",
            y="RelVol (x TB20)",
            color="Điểm Tổng Hợp",
            color_continuous_scale="Viridis",
            title="Top 15 Cổ phiếu Đột biến Thanh khoản so với TB20 phiên"
        )
        fig_bar.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Mức TB 20 phiên (1.0x)")
        fig_bar.update_layout(height=420)
        st.plotly_chart(fig_bar, use_container_width=True)

# TAB 3: SOI KÈO CHI TIẾT MÃ
with tab_detail:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        selected_symbol = st.selectbox("Chọn mã cổ phiếu phân tích sâu:", df_all["Mã CP"].tolist())
    
    selected_snap = snapshot_dict[selected_symbol]
    selected_row = df_all[df_all["Mã CP"] == selected_symbol].iloc[0]

    col_info, col_radar = st.columns([1, 1])

    with col_info:
        st.markdown(f"### 📌 Phân tích vi cấu trúc: **{selected_symbol}**")
        st.markdown(f"**Giá khớp gần nhất:** `{selected_snap.last_price:,.0f} VNĐ` ({selected_snap.pct_change:+.2f}%)")
        st.markdown(f"**Xếp hạng:** <span class='badge-top-buy'>{selected_row['Phân Hạng']}</span> (Điểm tổng hợp: **{selected_row['Điểm Tổng Hợp']} / 100**)", unsafe_allow_html=True)
        st.markdown(f"**Thuyết minh:** {selected_row['Tín hiệu phân tích']}")
        
        st.markdown("#### 📖 Chi tiết Sổ lệnh 3 Bước giá (Top 3 Bids & Asks)")
        ob = selected_snap.order_book
        
        col_bids, col_asks = st.columns(2)
        with col_bids:
            st.markdown("**BÊN MUA (BIDS)**")
            bid_df = pd.DataFrame([{"Giá": f"{b.price:,.0f}", "KL": f"{b.volume:,}"} for b in ob.bids])
            st.table(bid_df)
        with col_asks:
            st.markdown("**BÊN BÁN (ASKS)**")
            ask_df = pd.DataFrame([{"Giá": f"{a.price:,.0f}", "KL": f"{a.volume:,}"} for a in ob.asks])
            st.table(ask_df)

        tot_bid = sum(b.volume for b in ob.bids)
        tot_ask = sum(a.volume for a in ob.asks)
        bid_ratio = tot_bid / max(1, tot_bid + tot_ask)
        st.progress(bid_ratio, text=f"Tỷ lệ Lực Mua vs Bán: {bid_ratio:.1%} Cầu Mua - {1-bid_ratio:.1%} Cung Bán")

    with col_radar:
        st.markdown("#### 🕸️ Biểu đồ Radar 4 Trụ Cột Đa Nhân Tố")
        categories = ['Động lượng Giá', 'Thanh khoản & Vol', 'Khối ngoại', 'Sổ lệnh (OBI)']
        scores = [
            selected_row["Động lượng"],
            selected_row["Thanh khoản"],
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
    ### 📐 Phương pháp luận Tài chính & Cơ sở Định lượng
    
    Hệ thống giải quyết bài toán định lượng tín hiệu giao dịch ngắn hạn cho nhà đầu tư bằng cách kết hợp **Lý thuyết Vi cấu trúc thị trường (Market Microstructure)** và **Mô hình Đa nhân tố (Multi-Factor Scoring Model)**:
    
    1. **Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI):**
       $$OBI = \\frac{\\sum_{i=1}^3 \\text{BidVol}_i - \\sum_{i=1}^3 \\text{AskVol}_i}{\\sum_{i=1}^3 \\text{BidVol}_i + \\sum_{i=1}^3 \\text{AskVol}_i} \\in [-1.0, 1.0]$$
       *Cơ sở tài chính:* Trong khung thời gian ngắn hạn, áp lực đặt lệnh tại các bước giá tốt nhất phản ánh cung-cầu tức thời. Khi $OBI > 0$, lượng đặt mua áp đảo lượng đặt bán, tạo lực đẩy giá tăng ngắn hạn.
    
    2. **Đột biến Khối lượng (Relative Volume - RelVol):**
       $$\\text{RelVol} = \\frac{\\text{Volume}}{\\text{MA}_{20}(\\text{Volume})}$$
       *Cơ sở tài chính:* Tín hiệu bứt phá giá chỉ thực sự tin cậy khi đi kèm sự gia tăng của khối lượng giao dịch nhằm hấp thụ thanh khoản trượt giá (Slippage risk).
    
    3. **Dòng tiền Nước ngoài (Foreign Flow Impact):**
       $$\\text{Foreign Impact} = \\frac{\\text{Foreign Net Value}}{\\text{Total Traded Value}}$$
       *Cơ sở tài chính:* Dòng vốn ngoại đóng vai trò định hướng tâm lý và nâng đỡ thanh khoản đáng kể tại các mã Bluechips trên sàn HOSE.
    
    4. **Điểm Xếp Hạng Tổng Hợp (Composite Factor Score):**
       $$\\text{Composite Score} = 0.25 \\times S_{\\text{Mom}} + 0.25 \\times S_{\\text{Liq}} + 0.25 \\times S_{\\text{For}} + 0.25 \\times S_{\\text{OBI}}$$
       Thang điểm từ 0 đến 100. Ngưỡng $\\ge 70$ điểm kích hoạt phân tầng khuyến nghị **Top Buy**.
    
    ---
    
    ### ⚠️ Khuyến cáo Rủi ro & Miễn trừ Trách nhiệm Học thuật
    - **Mục đích đồ án:** Đây là sản phẩm nghiên cứu ứng dụng công nghệ tài chính phục vụ học phần *Gói phần mềm ứng dụng cho tài chính 1* tại Trường Đại học Kinh tế - Luật (UEL).
    - **Không phải khuyến nghị đầu tư:** Mọi dữ liệu, phân tích, xếp hạng và tín hiệu trên bảng điều khiển chỉ mang tính chất tham khảo học thuật, không cấu thành bất kỳ lời chào mua/bán hay tư vấn đầu tư tài chính tiền thật nào.
    - **Giới hạn mô hình:** Mô hình vi cấu trúc OBI phản ánh trạng thái ngắn hạn trong phiên, các lệnh ảo (spoofing) có thể được hủy bất cứ lúc nào trước khi khớp. Nhà đầu tư chịu hoàn toàn trách nhiệm đối với quyết định giao dịch của mình.
    """)
