"""
Ứng dụng Bảng điều khiển Bộ lọc Cổ phiếu Thông minh (Smart Stock Screener).
Đồ án cá nhân: FinTech với VPBankS NEO API & SSI FastConnect Data.
Sinh viên thực hiện: Nguyễn Hà Yến Vy - K244141706.

Tính năng:
- 100% DỮ LIỆU THẬT THỜI GIAN THỰC (Toàn sàn HOSE, HNX, UPCOM, VN30).
- Biểu đồ nến OHLCV động tương tác (Plotly Interactive Candlestick Chart).
- Phân tích chi tiết danh sách mã 'Top Buy' và mã đạt tiêu chí lọc.
- Nhấp chọn tên mã để xem biểu đồ kỹ thuật và sổ lệnh tức thời.
- Toàn bộ bằng tiếng Việt chuẩn mực tài chính, loại bỏ thuật ngữ thừa.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

from src.neo_api.client import NeoApiClient
from src.analytics.ranking import MultiFactorRankingEngine

# Múi giờ Việt Nam
VN_TZ = timezone(timedelta(hours=7))

# Cấu hình trang giao diện
st.set_page_config(
    page_title="Bộ Lọc Cổ Phiếu Thông Minh | NEO API FinTech",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho phong cách tài chính chuyên nghiệp
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #475569;
        margin-bottom: 18px;
    }
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .tier-top-buy {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    .tier-accumulation {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
    .tier-caution {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_neo_client():
    client = NeoApiClient()
    client.authenticate()
    return client


def format_vnd(val):
    """Định dạng tiền tệ VNĐ dễ đọc."""
    if abs(val) >= 1e9:
        return f"{val/1e9:.2f} tỷ"
    elif abs(val) >= 1e6:
        return f"{val/1e6:.1f} triệu"
    return f"{val:,.0f} đ"


# Khởi tạo Client
client = get_neo_client()

# --- SIDEBAR: Cấu hình thị trường & Tiêu chí lọc ---
with st.sidebar:
    st.markdown("### 🏛️ THỊ TRƯỜNG & PHẠM VI")
    
    universe_choice = st.selectbox(
        "Chọn phạm vi cổ phiếu:",
        ["VN30 (30 Cổ phiếu vốn hóa lớn)", "HOSE (Toàn sàn TP.HCM)", "HNX (Sàn Hà Nội)", "UPCOM (Thị trường chưa niêm yết)"],
        index=0
    )
    
    # Map lựa chọn
    universe_map = {
        "VN30 (30 Cổ phiếu vốn hóa lớn)": "VN30",
        "HOSE (Toàn sàn TP.HCM)": "HOSE",
        "HNX (Sàn Hà Nội)": "HNX",
        "UPCOM (Thị trường chưa niêm yết)": "UPCOM"
    }
    selected_universe = universe_map[universe_choice]

    st.markdown("---")
    st.markdown("### 🔍 BỘ LỌC CHIẾN LƯỢC")
    
    filter_tier = st.multiselect(
        "Nhóm xếp hạng:",
        options=["Top Buy", "Accumulation", "Neutral", "Caution"],
        default=["Top Buy", "Accumulation"]
    )
    
    min_score = st.slider(
        "Điểm tổng hợp tối thiểu:",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="Thang điểm từ 0 đến 100 tổng hợp từ 4 nhân tố: Động lượng giá, Khối lượng đột biến, Dòng tiền khối ngoại và Độ lệch cung-cầu sổ lệnh. Đặt 50 nghĩa là chỉ lọc các mã đạt từ 50 điểm trở lên."
    )
    
    filter_obi_pos = st.checkbox("Chỉ lấy mã Lực Mua áp đảo (OBI > 0)", value=False)
    filter_vol_spike = st.checkbox("Chỉ lấy mã Khối lượng đột biến (RelVol >= 1.2x)", value=False)
    filter_foreign_buy = st.checkbox("Chỉ lấy mã Khối ngoại mua ròng", value=False)
    
    st.markdown("---")
    if st.button("🔄 Cập nhật dữ liệu trực tuyến", width='stretch'):
        st.cache_data.clear()
        st.rerun()

    st.caption("Dữ liệu trực tuyến 100% từ hạ tầng VPBankS NEO API & Bảng giá thị trường Việt Nam.")


# --- PHẦN TIÊU ĐỀ CHÍNH ---
now_vn = datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M:%S")
st.markdown('<div class="main-header">HỆ THỐNG XẾP HẠNG & LỌC CỔ PHIẾU THÔNG MINH ĐA NHÂN TỐ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Phân tích vi cấu trúc sổ lệnh (OBI), Đột biến thanh khoản và Dòng tiền khối ngoại | Dữ liệu trực tuyến thực tế: <b>{now_vn} (UTC+7)</b></div>', unsafe_allow_html=True)

# --- TẢI DỮ LIỆU THỰC TẾ ---
with st.spinner(f"Đang tải dữ liệu vi cấu trúc trực tuyến cho phạm vi {selected_universe}..."):
    snapshots = client.get_market_universe(universe=selected_universe)
    ranking_engine = MultiFactorRankingEngine()
    ranked_results = ranking_engine.rank_universe(snapshots)

if not snapshots:
    st.warning("Không có dữ liệu trả về từ máy chủ thị trường. Vui lòng bấm 'Cập nhật dữ liệu trực tuyến'.")
    st.stop()

# Xây dựng bảng dữ liệu
snapshot_dict = {s.symbol: s for s in snapshots}
data_rows = []
for r in ranked_results:
    snap = snapshot_dict.get(r.symbol)
    if not snap:
        continue
    
    # Lấy OBI từ order_book
    total_bid = sum(b.volume for b in snap.order_book.bids) if snap.order_book else 0
    total_ask = sum(a.volume for a in snap.order_book.asks) if snap.order_book else 0
    raw_obi = (total_bid - total_ask) / max(1, total_bid + total_ask)

    data_rows.append({
        "Mã CP": r.symbol,
        "Giá (VNĐ)": snap.last_price,
        "Thay đổi (%)": snap.pct_change,
        "Tổng Khối Lượng": snap.total_volume,
        "Tổng Giá Trị": snap.total_value,
        "Đột biến Vol": snap.total_volume / snap.avg_volume_20d if snap.avg_volume_20d > 0 else 1.0,
        "Độ lệch OBI": raw_obi,
        "Khối ngoại ròng": snap.foreign_trade.net_value if snap.foreign_trade else 0.0,
        "Điểm Tổng Hợp": r.composite_score,
        "Phân Hạng": r.ranking_tier,
        "Điểm Động Lượng": r.momentum_score,
        "Điểm Thanh Khoản": r.liquidity_score,
        "Điểm Khối Ngoại": r.foreign_score,
        "Điểm Cung-Cầu OBI": r.order_book_imbalance_score,
        "Tín Hiệu Nhận Định": r.signal_summary
    })

df_all = pd.DataFrame(data_rows)

# Lọc dữ liệu theo điều kiện người dùng chọn
df_filtered = df_all[df_all["Điểm Tổng Hợp"] >= min_score].copy()
if filter_tier:
    df_filtered = df_filtered[df_filtered["Phân Hạng"].isin(filter_tier)]
if filter_obi_pos:
    df_filtered = df_filtered[df_filtered["Độ lệch OBI"] > 0]
if filter_vol_spike:
    df_filtered = df_filtered[df_filtered["Đột biến Vol"] >= 1.2]
if filter_foreign_buy:
    df_filtered = df_filtered[df_filtered["Khối ngoại ròng"] > 0]

# --- THẺ THỐNG KÊ TỔNG QUAN ---
st.markdown("### 📊 Tổng Quan Độ Rộng & Trạng Thái Thị Trường")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

df_top_buy = df_all[df_all["Phân Hạng"] == "Top Buy"]
advances = (df_all["Thay đổi (%)"] > 0).sum()
declines = (df_all["Thay đổi (%)"] < 0).sum()
total_foreign = df_all["Khối ngoại ròng"].sum()

col_m1.metric("🏆 Số mã 'Top Buy'", f"{len(df_top_buy)} / {len(df_all)}", delta=f"{len(df_top_buy)/len(df_all):.1%} danh mục")
col_m2.metric("⚖️ Độ rộng Thị trường", f"{advances} Tăng / {declines} Giảm", delta=f"{advances - declines} mã chênh lệch")
col_m3.metric("🌐 Mua/Bán Ròng Khối Ngoại", format_vnd(total_foreign), delta="Dòng vốn ngoại")
col_m4.metric("🎯 Mã Đạt Tiêu Chí Lọc", f"{len(df_filtered)} / {len(df_all)}", delta=f"{len(df_filtered)/len(df_all):.1%} rổ lọc")

st.markdown("---")

# --- PHÂN KHU TƯƠNG TÁC: TAB GIAO DIỆN ---
tab_details, tab_screener, tab_viz, tab_method = st.tabs([
    "🔍 Danh Sách Chi Tiết & Biểu Đồ Nến Động",
    "📋 Bảng Xếp Hạng Đa Nhân Tố",
    "📈 Trực Quan Hóa Vi Cấu Trúc Toàn Rổ",
    "📚 Phương Pháp Định Lượng & Miễn Trừ"
])


# ==============================================================================
# TAB 1: HIỆN CỤ THỂ CHI TIẾT TOP BUY, MÃ ĐẠT TIÊU CHÍ VÀ BIỂU ĐỒ NẾN ĐỘNG TỪNG MÃ
# ==============================================================================
with tab_details:
    st.subheader("🎯 Danh Sách Chi Tiết Nhóm 'Top Buy' & Nhóm Đạt Tiêu Chí Lọc")
    
    col_group1, col_group2 = st.columns(2)
    
    with col_group1:
        st.markdown(f"#### 🏆 Nhóm Cổ Phiếu Đạt Chuẩn 'Top Buy' ({len(df_top_buy)} mã)")
        if not df_top_buy.empty:
            show_cols = ["Mã CP", "Giá (VNĐ)", "Thay đổi (%)", "Điểm Tổng Hợp", "Độ lệch OBI", "Tín Hiệu Nhận Định"]
            st.dataframe(
                df_top_buy[show_cols].style.format({
                    "Giá (VNĐ)": "{:,.0f}",
                    "Thay đổi (%)": "{:+.2f}%",
                    "Điểm Tổng Hợp": "{:.1f}",
                    "Độ lệch OBI": "{:+.1%}"
                }),
                width='stretch',
                height=220
            )
        else:
            st.info("Hiện không có mã nào đạt ngưỡng xếp hạng 'Top Buy' (>= 70 điểm).")

    with col_group2:
        st.markdown(f"#### 🎯 Nhóm Cổ Phiếu Thỏa Mãn Bộ Lọc Hiện Tại ({len(df_filtered)} mã)")
        if not df_filtered.empty:
            show_cols_f = ["Mã CP", "Giá (VNĐ)", "Thay đổi (%)", "Điểm Tổng Hợp", "Phân Hạng", "Tín Hiệu Nhận Định"]
            st.dataframe(
                df_filtered[show_cols_f].style.format({
                    "Giá (VNĐ)": "{:,.0f}",
                    "Thay đổi (%)": "{:+.2f}%",
                    "Điểm Tổng Hợp": "{:.1f}"
                }),
                width='stretch',
                height=220
            )
        else:
            st.info("Không có mã nào thỏa mãn tiêu chí lọc bạn đang thiết lập.")

    st.markdown("---")
    st.subheader("📈 Xem Biểu Đồ Kỹ Thuật Động & Sổ Lệnh Chi Tiết Từng Mã")
    
    # Chọn mã để xem chi tiết
    all_symbols = df_all["Mã CP"].tolist()
    default_sym = df_filtered["Mã CP"].iloc[0] if not df_filtered.empty else (df_top_buy["Mã CP"].iloc[0] if not df_top_buy.empty else all_symbols[0])
    
    selected_sym = st.selectbox(
        "👉 Bấm chọn mã cổ phiếu cần xem biểu đồ động & sổ lệnh:",
        all_symbols,
        index=all_symbols.index(default_sym) if default_sym in all_symbols else 0
    )

    sym_snap = snapshot_dict[selected_sym]
    sym_row = df_all[df_all["Mã CP"] == selected_sym].iloc[0]

    col_chart, col_depth = st.columns([3, 2])

    with col_chart:
        st.markdown(f"#### 🕯️ Biểu Đồ Nến Kỹ Thuật & Khối Lượng Trực Tuyến: **{selected_sym}**")
        
        # Tải dữ liệu nến lịch sử thực tế
        with st.spinner(f"Đang tải lịch sử giá thực tế của {selected_sym}..."):
            ohlc_data = client.get_stock_history_ohlc(selected_sym, days=60)

        if ohlc_data and "t" in ohlc_data:
            # Chuyển đổi timestamp thành ngày
            dates = [datetime.fromtimestamp(ts, tz=VN_TZ).strftime("%Y-%m-%d") for ts in ohlc_data["t"]]
            fig_candle = go.Figure()
            
            # Vẽ nến Candlestick
            fig_candle.add_trace(go.Candlestick(
                x=dates,
                open=ohlc_data.get("o", []),
                high=ohlc_data.get("h", []),
                low=ohlc_data.get("l", []),
                close=ohlc_data.get("c", []),
                name="Giá nến (VNĐ)",
                increasing_line_color="#16A34A",
                decreasing_line_color="#DC2626"
            ))

            fig_candle.update_layout(
                title=f"Diễn biến giá {selected_sym} (60 phiên gần nhất)",
                yaxis_title="Giá (VNĐ)",
                xaxis_rangeslider_visible=False,
                height=420,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_candle, width='stretch')
        else:
            st.info(f"Đang hiển thị thông số phiên khớp lệnh gần nhất của {selected_sym}:")
            c1, c2, c3 = st.columns(3)
            c1.metric("Giá Khớp", f"{sym_snap.last_price:,.0f} đ", f"{sym_snap.pct_change:+.2f}%")
            c2.metric("Cao Nhất / Thấp Nhất", f"{sym_snap.high_price:,.0f} / {sym_snap.low_price:,.0f}")
            c3.metric("Tổng Khối Lượng", f"{sym_snap.total_volume:,} cp")

    with col_depth:
        st.markdown(f"#### 📖 Sổ Lệnh 3 Bước Giá Thực Tế (Top 3 Bids/Asks): **{selected_sym}**")
        st.markdown(f"**Xếp hạng:** <span class='tier-top-buy'>{sym_row['Phân Hạng']}</span> (Điểm Tổng Hợp: **{sym_row['Điểm Tổng Hợp']} / 100**)", unsafe_allow_html=True)
        st.markdown(f"**Nhận định định lượng:** {sym_row['Tín Hiệu Nhận Định']}")

        ob = sym_snap.order_book
        if ob:
            col_b, col_a = st.columns(2)
            with col_b:
                st.markdown("**BÊN MUA (DƯ MUA)**")
                bid_table = pd.DataFrame([{"Giá Mua": f"{b.price:,.0f}", "KL Mua": f"{b.volume:,}"} for b in ob.bids])
                st.table(bid_table)
            with col_a:
                st.markdown("**BÊN BÁN (DƯ BÁN)**")
                ask_table = pd.DataFrame([{"Giá Bán": f"{a.price:,.0f}", "KL Bán": f"{a.volume:,}"} for a in ob.asks])
                st.table(ask_table)

            total_b = sum(b.volume for b in ob.bids)
            total_a = sum(a.volume for a in ob.asks)
            ratio = total_b / max(1, total_b + total_a)
            st.progress(ratio, text=f"Tương quan Cung - Cầu sổ lệnh: {ratio:.1%} Cầu Mua | {1-ratio:.1%} Cung Bán")
        
        # Biểu đồ Radar 4 trụ cột
        st.markdown("#### 🕸️ Biểu Đồ Radar 4 Trụ Cột Đa Nhân Tố")
        radar_categories = ["Động Lượng Giá", "Thanh Khoản", "Khối Ngoại", "Cung-Cầu Sổ Lệnh"]
        radar_values = [
            sym_row["Điểm Động Lượng"],
            sym_row["Điểm Thanh Khoản"],
            sym_row["Điểm Khối Ngoại"],
            sym_row["Điểm Cung-Cầu OBI"]
        ]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_values + [radar_values[0]],
            theta=radar_categories + [radar_categories[0]],
            fill='toself',
            name=selected_sym,
            line_color='#2563EB'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=280,
            margin=dict(l=30, r=30, t=20, b=20)
        )
        st.plotly_chart(fig_radar, width='stretch')


# ==============================================================================
# TAB 2: BẢNG LỌC REALTIME ĐẦY ĐỦ
# ==============================================================================
with tab_screener:
    st.subheader("📋 Bảng Xếp Hạng Toàn Bộ Cổ Phiếu Theo Điểm Tổng Hợp")
    
    def highlight_tier(val):
        if val == "Top Buy":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "Accumulation":
            return "background-color: #E0F2FE; color: #0369A1;"
        elif val == "Caution":
            return "background-color: #FEE2E2; color: #991B1B;"
        return ""

    format_mapping = {
        "Giá (VNĐ)": "{:,.0f}",
        "Thay đổi (%)": "{:+.2f}%",
        "Tổng Khối Lượng": "{:,.0f}",
        "Tổng Giá Trị": lambda x: format_vnd(x),
        "Đột biến Vol": "{:.2f}x",
        "Độ lệch OBI": "{:+.1%}",
        "Khối ngoại ròng": lambda x: format_vnd(x),
        "Điểm Tổng Hợp": "{:.1f}",
        "Điểm Động Lượng": "{:.1f}",
        "Điểm Thanh Khoản": "{:.1f}",
        "Điểm Khối Ngoại": "{:.1f}",
        "Điểm Cung-Cầu OBI": "{:.1f}"
    }

    styled_screener = df_filtered.style.map(highlight_tier, subset=["Phân Hạng"]).format(format_mapping)
    st.dataframe(styled_screener, width='stretch', height=480)
    st.caption("💡 Mẹo: Bấm vào tiêu đề bất kỳ cột nào để sắp xếp tăng dần hoặc giảm dần.")


# ==============================================================================
# TAB 3: TRỰC QUAN HÓA VI CẤU TRÚC TOÀN RỔ (BIỂU ĐỒ ĐỘNG PLOTLY)
# ==============================================================================
with tab_viz:
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown("#### 🎯 Bản Đồ Tương Quan: Độ Lệch Sổ Lệnh (OBI) vs Biến Động Giá (%)")
        fig_scatter = px.scatter(
            df_all,
            x="Độ lệch OBI",
            y="Thay đổi (%)",
            size="Điểm Tổng Hợp",
            color="Phân Hạng",
            hover_name="Mã CP",
            hover_data={
                "Giá (VNĐ)": ":,.0f",
                "Đột biến Vol": ":.2f",
                "Khối ngoại ròng": True
            },
            color_discrete_map={
                "Top Buy": "#16A34A",
                "Accumulation": "#0284C7",
                "Neutral": "#64748B",
                "Caution": "#DC2626"
            },
            title="Biểu đồ phân tán động OBI vs Biến động Giá"
        )
        fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_scatter.update_layout(height=420)
        st.plotly_chart(fig_scatter, width='stretch')
        st.caption("Góc trên bên phải: Cổ phiếu tăng giá mạnh kèm lực Mua sổ lệnh áp đảo (Tín hiệu bền vững nhất).")

    with col_v2:
        st.markdown("#### 🌊 Top 15 Cổ Phiếu Đột Biến Khối Lượng Giao Dịch")
        top_vol = df_all.sort_values(by="Đột biến Vol", ascending=False).head(15)
        fig_bar = px.bar(
            top_vol,
            x="Mã CP",
            y="Đột biến Vol",
            color="Điểm Tổng Hợp",
            color_continuous_scale="Blues",
            title="Khối lượng tích lũy so với trung bình 20 phiên"
        )
        fig_bar.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Mức TB 20 phiên (1.0x)")
        fig_bar.update_layout(height=420)
        st.plotly_chart(fig_bar, width='stretch')


# ==============================================================================
# TAB 4: PHƯƠNG PHÁP ĐỊNH LƯỢNG & MIỄN TRỪ TRÁCH NHIỆM
# ==============================================================================
with tab_method:
    st.markdown("""
    ### 📐 Phương Pháp Luận Tài Chính & Cơ Sở Định Lượng
    
    Hệ thống giải quyết bài toán phát hiện dòng tiền thông minh bằng cách kết hợp **Lý thuyết Vi cấu trúc thị trường (Market Microstructure)** và **Mô hình Xếp hạng Đa nhân tố Chuẩn hóa Phân vị (Cross-Sectional Percentile Multi-Factor Model)**:
    
    1. **Độ lệch Cung - Cầu Sổ lệnh Có Trọng Số (Weighted Order Book Imbalance - OBI):**
       $$OBI = \\frac{\\sum_{i=1}^3 w_i \\text{BidVol}_i - \\sum_{i=1}^3 w_i \\text{AskVol}_i}{\\sum_{i=1}^3 w_i \\text{BidVol}_i + \\sum_{i=1}^3 w_i \\text{AskVol}_i} \\in [-1.0, 1.0]$$
       *Trong đó:* $w_1 = 0.5$ (Bước giá 1 sát khớp nhất), $w_2 = 0.3$, $w_3 = 0.2$.  
       *Ý nghĩa tài chính:* Khắc phục nhược điểm cộng cào bằng khối lượng. Khi $OBI > 0$, lượng đặt mua áp đảo lượng đặt bán, tạo lực đẩy tăng giá ngắn hạn.
    
    2. **Đột biến Khối lượng (Relative Volume - RelVol):**
       $$\\text{RelVol} = \\frac{\\text{Khối Lượng Khớp}}{\\text{Khối Lượng Trung Bình 20 Phiên}}$$
       *Ý nghĩa tài chính:* Tín hiệu tăng giá đi kèm khối lượng lớn giúp hấp thụ rủi ro trượt giá và đảm bảo tính bền vững của xu hướng.
    
    3. **Dòng tiền Khối ngoại (Foreign Net Flow Impact):**
       Đo lường giá trị mua/bán ròng và tỷ trọng nâng đỡ của khối ngoại trên tổng thanh khoản khớp lệnh.
    
    4. **Thuật toán Xếp Hạng Chuẩn Hóa Phân Vị (Percentile Ranking Score: 0 - 100):**
       $$\\text{Điểm Tổng Hợp} = 0.25 \\times S_{\\text{Động Lượng}} + 0.25 \\times S_{\\text{Thanh Khoản}} + 0.25 \\times S_{\\text{Khối Ngoại}} + 0.25 \\times S_{\\text{OBI}}$$
       Thích ứng tự động với mọi trạng thái của thị trường (Tăng, Giảm, Đi ngang) mà không bị lỗi cắt ngưỡng cứng.
    
    ---
    
    ### ⚠️ Khuyến Cáo Rủi Ro & Miễn Trừ Trách Nhiệm Học Thuật
    - **Mục đích đồ án:** Đây là sản phẩm nghiên cứu ứng dụng công nghệ tài chính phục vụ học phần *Gói phần mềm ứng dụng cho tài chính 1* tại Trường Đại học Kinh tế - Luật (ĐHQG-HCM).
    - **Không phải khuyến nghị đầu tư:** Mọi dữ liệu, phân tích, xếp hạng và tín hiệu trên bảng điều khiển chỉ mang tính chất tham khảo học thuật, không cấu thành bất kỳ lời chào mua/bán hay tư vấn đầu tư tài chính tiền thật nào.
    - **Giới hạn mô hình:** Mô hình vi cấu trúc OBI phản ánh trạng thái ngắn hạn trong phiên, các lệnh ảo có thể bị hủy trước khi khớp. Nhà đầu tư tự chịu trách nhiệm đối với quyết định giao dịch của mình.
    """)
