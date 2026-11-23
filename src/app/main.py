"""
Ứng dụng Bảng điều khiển Bộ lọc Cổ phiếu Thông minh (Smart Stock Screener).
Hệ thống Hỗ trợ Quyết định Đầu tư & Tư vấn Môi giới Dựa trên Vi cấu trúc Thị trường.
Đồ án cá nhân: FinTech với VPBankS NEO API & SSI FastConnect API v3.
Sinh viên thực hiện: Nguyễn Hà Yến Vy - K244141706.
Khoa Tài chính - Ngân hàng, Trường Đại học Kinh tế - Luật (UEL).
"""
from datetime import datetime, timedelta, timezone

import numpy as np
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
    .strategy-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    .badge-buy {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-hold {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-alert {
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
    st.subheader("🎯 Chiến lược Phân bổ & Bộ lọc")
    filter_strategy = st.multiselect(
        "Chiến lược hành động:",
        options=["🚀 Mua Bứt Phá", "🛡️ Tích Lũy Gom", "⚪ Quan Sát", "⚠️ Cảnh Báo Bán"],
        default=["🚀 Mua Bứt Phá", "🛡️ Tích Lũy Gom"]
    )
    
    min_score = st.slider("Điểm tổng hợp tối thiểu:", min_value=0, max_value=100, value=50, step=5)
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

col_title, col_status = st.columns([2.7, 1.3])
with col_title:
    st.markdown('<div class="main-header">HỆ THỐNG XẾP HẠNG & HỖ TRỢ RA QUYẾT ĐỊNH ĐẦU TƯ FINTECH</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">'
        f'Khoa Tài chính - Ngân hàng UEL | <b>100% Dữ liệu Thực tế (Zero Mock)</b> | Cập nhật: <b>{now_vn}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_status:
    provider_name = conn_status["active_provider"]
    is_neo = "VPBankS" in provider_name
    badge_icon = "🟢" if is_neo else "🔵"
    st.markdown(f"""
    <div class="status-box">
        <b>{badge_icon} Nguồn cấp:</b> {provider_name}<br>
        <b>🛡️ IP Whitelist:</b> <code>{conn_status['whitelisted_ip']}</code><br>
        <b>💻 IP Trạm kết nối:</b> <code>{conn_status['current_ip']}</code><br>
        <b>🔐 Khóa SSI FastConnect:</b> {'Đã xác thực v3' if settings.SSI_API_KEY else 'Cổng iBoard'}
    </div>
    """, unsafe_allow_html=True)


# --- TÍNH TOÁN XẾP HẠNG ĐA NHÂN TỐ & CHIẾN LƯỢC HÀNH ĐỘNG THỰC CHIẾN ---
ranking_engine = MultiFactorRankingEngine()
ranked_results = ranking_engine.rank_universe(snapshots)

snapshot_dict = {s.symbol: s for s in snapshots}
data_rows = []
all_total_bid_vol = 0
all_total_ask_vol = 0

for r in ranked_results:
    snap = snapshot_dict[r.symbol]
    order_book = snap.order_book
    bid_volume = sum(level.volume for level in order_book.bids) if order_book else 0
    ask_volume = sum(level.volume for level in order_book.asks) if order_book else 0
    all_total_bid_vol += bid_volume
    all_total_ask_vol += ask_volume
    
    obi_value = (bid_volume - ask_volume) / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else float("nan")
    foreign_net = snap.foreign_trade.net_value if snap.foreign_trade else None
    score = r.composite_score if r.composite_score is not None else float("nan")
    
    # 🎯 PHÂN LOẠI CHIẾN LƯỢC HÀNH ĐỘNG THỰC CHIẾN (Actionable Playbook)
    if pd.notna(score) and score >= 70 and pd.notna(obi_value) and obi_value > 0.15:
        strategy = "🚀 Mua Bứt Phá"
        alloc = "15% - 20% NAV"
    elif pd.notna(score) and score >= 55 and pd.notna(obi_value) and obi_value > 0.0:
        strategy = "🛡️ Tích Lũy Gom"
        alloc = "10% - 15% NAV"
    elif pd.notna(obi_value) and obi_value < -0.20 or (pd.notna(score) and score < 40):
        strategy = "⚠️ Cảnh Báo Bán"
        alloc = "0% (Đứng ngoài)"
    else:
        strategy = "⚪ Quan Sát"
        alloc = "0% - 5% NAV"

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
        "Điểm Tổng Hợp": score,
        "Phân Hạng": r.ranking_tier,
        "Chiến lược": strategy,
        "Tỷ trọng khuyến nghị": alloc,
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
if filter_strategy:
    df_filtered = df_filtered[df_filtered["Chiến lược"].isin(filter_strategy)]
if filter_normal_status:
    df_filtered = df_filtered[df_filtered["Trạng thái"] == "NORMAL"]
if filter_obi_positive:
    df_filtered = df_filtered[df_filtered["OBI Sổ lệnh"] > 0]
if filter_foreign_buy:
    df_filtered = df_filtered[df_filtered["Khối ngoại ròng"] > 0]

# --- METRIC CARDS & ĐỒNG HỒ ÁP LỰC VI CẤU TRÚC TOÀN THỊ TRƯỜNG ---
st.markdown("### 📊 Tổng quan Áp lực Vi cấu trúc & Sức mạnh Dòng tiền")

col_gauge, col_m1, col_m2, col_m3 = st.columns([1.5, 1, 1, 1])

# Tính toán Market OBI
market_obi = ((all_total_bid_vol - all_total_ask_vol) / (all_total_bid_vol + all_total_ask_vol) * 100) if (all_total_bid_vol + all_total_ask_vol) > 0 else 0

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=market_obi,
        number={'suffix': "%", 'valueformat': "+.1f"},
        title={'text': "<b>Áp lực Vi cấu trúc Rổ Thị trường (Market OBI)</b>", 'font': {'size': 13}},
        gauge={
            'axis': {'range': [-100, 100]},
            'bar': {'color': "#16A34A" if market_obi > 0 else "#DC2626"},
            'steps': [
                {'range': [-100, -20], 'color': '#FEE2E2'},
                {'range': [-20, 20], 'color': '#F1F5F9'},
                {'range': [20, 100], 'color': '#DCFCE7'}
            ],
            'threshold': {'line': {'color': "#2563EB", 'width': 3}, 'thickness': 0.8, 'value': market_obi}
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=15, r=15, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_m1:
    strong_count = (df_all["Chiến lược"] == "🚀 Mua Bứt Phá").sum()
    st.metric("🚀 Tín hiệu Mua Bứt Phá", f"{strong_count} mã", delta="Hội tụ Cầu & Dòng tiền")
    advances = (df_all["Thay đổi (%)"] > 0).sum()
    declines = (df_all["Thay đổi (%)"] < 0).sum()
    st.metric("⚖️ Độ rộng Thị trường", f"{advances} Tăng / {declines} Giảm", delta=f"{advances - declines} mã")

with col_m2:
    accum_count = (df_all["Chiến lược"] == "🛡️ Tích Lũy Gom").sum()
    st.metric("🛡️ Tín hiệu Tích Lũy Gom", f"{accum_count} mã", delta="Dòng tiền âm thầm gom")
    foreign_net_values = df_all["Khối ngoại ròng"].dropna()
    total_foreign_net = foreign_net_values.sum() if not foreign_net_values.empty else None
    st.metric("🌐 Khối Ngoại Mua/Bán Ròng", format_currency(total_foreign_net) if total_foreign_net is not None else "N/A", delta="Tác động dòng vốn")

with col_m3:
    alert_count = (df_all["Chiến lược"] == "⚠️ Cảnh Báo Bán").sum()
    st.metric("⚠️ Cảnh báo Đè Bán", f"{alert_count} mã", delta="Cung bán đè sổ lệnh")
    st.metric("🎯 Mã đạt Tiêu chí Lọc", f"{len(df_filtered)} / {len(df_all)} mã", delta=f"{len(df_filtered)/len(df_all):.0%}")

st.markdown("---")

# --- TABS GIAO DIỆN CHÍNH ---
tab_screener, tab_viz, tab_detail, tab_broker, tab_method = st.tabs([
    "📋 Bảng Lọc & Chiến Lược Thực Chiến",
    "📈 Trực Quan Hóa Vi Cấu Trúc",
    "🔬 Soi Kèo Sổ Lệnh & Quản Trị Rủi Ro",
    "📢 Bản Tin Tư Vấn Dành Cho Môi Giới",
    "📚 Phương Pháp Luận & Miễn Trừ"
])

# TAB 1: BẢNG LỌC REALTIME
with tab_screener:
    st.subheader(f"Bảng Lọc Cổ phiếu Định Lượng & Chiến Lược Hành Động ({len(df_filtered)} / {len(df_all)} mã)")
    
    def highlight_strategy(val):
        if "Mua Bứt Phá" in str(val):
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif "Tích Lũy Gom" in str(val):
            return "background-color: #E0F2FE; color: #0369A1; font-weight: bold;"
        elif "Cảnh Báo Bán" in str(val):
            return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
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

    display_cols = [
        "Mã CP", "Giá (VNĐ)", "Thay đổi (%)", "Chiến lược", "Tỷ trọng khuyến nghị",
        "Điểm Tổng Hợp", "OBI Sổ lệnh", "Khối ngoại ròng", "Tổng GTGD", "Tín hiệu phân tích"
    ]
    styled_df = df_filtered[display_cols].style.map(highlight_strategy, subset=["Chiến lược"]).format(format_dict)
    st.dataframe(styled_df, use_container_width=True, height=480)
    st.caption("💡 Mẹo: Bấm vào tiêu đề cột để sắp xếp theo Điểm Tổng Hợp, OBI Sổ lệnh hoặc Khối ngoại.")

# TAB 2: TRỰC QUAN HÓA VI CẤU TRÚC
with tab_viz:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🎯 Bản đồ Nhiệt Tương quan: Độ lệch Sổ lệnh (OBI) vs Biến động Giá (%)")
        fig_scatter = px.scatter(
            df_all,
            x="OBI Sổ lệnh",
            y="Thay đổi (%)",
            size="Điểm Tổng Hợp",
            color="Chiến lược",
            hover_name="Mã CP",
            hover_data=["Giá (VNĐ)", "Tổng GTGD"],
            color_discrete_map={
                "🚀 Mua Bứt Phá": "#16A34A",
                "🛡️ Tích Lũy Gom": "#0284C7",
                "⚪ Quan Sát": "#64748B",
                "⚠️ Cảnh Báo Bán": "#DC2626"
            },
            title="Mối quan hệ giữa Áp lực Gom Mua/Đè Bán Top 3 và Biến động Giá"
        )
        fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_scatter.update_layout(height=430)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Góc phần tư trên cùng bên phải (OBI > 0 và Giá tăng) là khu vực dòng tiền tổ chức bứt phá rõ rệt nhất.")

    with col_chart2:
        st.markdown("#### 🌊 Phân bổ Thanh khoản Phiên Thực tế Top 15 Cổ phiếu")
        fig_bar = px.bar(
            df_all.sort_values(by="Tổng GTGD", ascending=False).head(15),
            x="Mã CP",
            y="Tổng GTGD",
            color="Điểm Tổng Hợp",
            color_continuous_scale="Viridis",
            title="Top 15 cổ phiếu theo giá trị giao dịch thực (VNĐ)"
        )
        fig_bar.update_layout(height=430)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Màu sắc thể hiện Điểm Tổng Hợp đa nhân tố; độ cao cột thể hiện quy mô thanh khoản tiền thật.")

# TAB 3: SOI KÈO SỔ LỆNH & QUẢN TRỊ RỦI RO
with tab_detail:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        symbol_list = df_all["Mã CP"].tolist()
        selected_symbol = st.selectbox("Chọn mã cổ phiếu phân tích sâu:", symbol_list)
    
    if selected_symbol and selected_symbol in snapshot_dict:
        selected_snap = snapshot_dict[selected_symbol]
        selected_row = df_all[df_all["Mã CP"] == selected_symbol].iloc[0]

        col_info, col_risk = st.columns([1.1, 0.9])

        with col_info:
            st.markdown(f"### 📌 Bóc tách Vi cấu trúc: **{selected_symbol}**")
            pct_display = f"{selected_snap.pct_change:+.2f}%" if selected_snap.pct_change is not None else "N/A"
            st.markdown(f"**Giá khớp lệnh:** `{selected_snap.last_price:,.0f} VNĐ` ({pct_display}) | **Chiến lược:** **{selected_row['Chiến lược']}**")
            st.markdown(f"**Điểm Đa nhân tố:** **{selected_row['Điểm Tổng Hợp']} / 100** | **Tỷ trọng đề xuất:** `{selected_row['Tỷ trọng khuyến nghị']}`")
            st.markdown(f"**Thuyết minh:** {selected_row['Tín hiệu phân tích']}")

            st.markdown("#### 📖 Sổ lệnh Độ sâu 3 Bước giá (Top 3 Bids & Asks)")
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
                st.progress(bid_ratio, text=f"Lực Cầu Mua Top 3: {bid_ratio:.1%} | Lực Cung Bán Top 3: {1-bid_ratio:.1%}")

        with col_risk:
            st.markdown("#### 🛡️ Khung Quản Trị Rủi Ro & Kế Hoạch Vào Lệnh (Execution Playbook)")
            
            p_last = selected_snap.last_price
            p_high = selected_snap.high_price or p_last
            p_low = selected_snap.low_price or p_last
            day_range = max(p_high - p_low, p_last * 0.015)
            
            # Tính toán các ngưỡng kỹ thuật
            buy_zone = f"{p_last * 0.995:,.0f} - {p_last:,.0f}"
            target_price = p_last + (day_range * 1.5)
            stop_loss = max(p_low, p_last - day_range)
            reward_risk = (target_price - p_last) / max(p_last - stop_loss, 1)
            
            st.markdown(f"""
            <div class="strategy-card">
                <b>🎯 Kế hoạch giao dịch thực chiến:</b><br>
                • <b>Vùng giải ngân đề xuất:</b> <code>{buy_zone} VNĐ</code><br>
                • <b>Mục tiêu lợi nhuận ngắn hạn (Target):</b> <code style="color: #166534;">{target_price:,.0f} VNĐ (+{(target_price/p_last - 1)*100:.1f}%)</code><br>
                • <b>Ngưỡng chặn lỗ kỷ luật (Stop-Loss):</b> <code style="color: #991B1B;">{stop_loss:,.0f} VNĐ (-{(1 - stop_loss/p_last)*100:.1f}%)</code><br>
                • <b>Tỷ lệ Lợi nhuận / Rủi ro (R:R):</b> <b>{reward_risk:.2f} : 1</b><br>
                • <b>Tỷ trọng danh mục tối đa:</b> <b>{selected_row['Tỷ trọng khuyến nghị']}</b>
            </div>
            """, unsafe_allow_html=True)

            # Radar Chart
            st.markdown("##### 🕸️ Radar Trụ Cột Vi Cấu Trúc")
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
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=270, margin=dict(l=20, r=20, t=10, b=10))
            st.plotly_chart(fig_radar, use_container_width=True)

# TAB 4: BẢN TIN TƯ VẤN DÀNH CHO MÔI GIỚI (BROKER TOOLKIT)
with tab_broker:
    st.markdown("### 📢 Bộ Công Cụ Tạo Nhanh Bản Tin Tư Vấn Dành Cho Môi Giới (Broker Flash Note)")
    st.caption("Tự động hóa hoàn toàn việc soạn thảo bản tin tư vấn khuyến nghị gửi khách hàng qua Zalo / Telegram / Email ngay trong phiên.")
    
    col_b_sel, col_b_btn = st.columns([2, 1])
    with col_b_sel:
        broker_symbol = st.selectbox("Chọn mã cổ phiếu cần tạo bản tin tư vấn:", df_all["Mã CP"].tolist(), key="broker_symbol_select")
    
    b_snap = snapshot_dict[broker_symbol]
    b_row = df_all[df_all["Mã CP"] == broker_symbol].iloc[0]
    
    b_p_last = b_snap.last_price
    b_p_high = b_snap.high_price or b_p_last
    b_p_low = b_snap.low_price or b_p_last
    b_range = max(b_p_high - b_p_low, b_p_last * 0.015)
    b_target = b_p_last + (b_range * 1.5)
    b_stop = max(b_p_low, b_p_last - b_range)
    
    obi_txt = f"{b_row['OBI Sổ lệnh']:+.1%}" if pd.notna(b_row['OBI Sổ lệnh']) else "Cân bằng"
    foreign_txt = format_currency(b_row['Khối ngoại ròng'])
    
    flash_note_content = f"""📢 [BẢN TIN TƯ VẤN NHANH - KHUYẾN NGHỊ TRONG PHIÊN]
Mã cổ phiếu: {broker_symbol} | Sàn: {b_snap.market_code or 'HOSE'}
Thời gian cập nhật: {now_vn}
Giá khớp hiện tại: {b_p_last:,.0f} VNĐ ({b_snap.pct_change:+.2f}%)
--------------------------------------------------
🔍 PHÂN TÍCH VI CẤU TRÚC DÒNG TIỀN:
1. Độ lệch Sổ lệnh (OBI Top 3): {obi_txt} ({'Lực gom mua áp đảo' if b_row['OBI Sổ lệnh'] > 0 else 'Cung bán đè'})
2. Dòng tiền Khối ngoại: {foreign_txt} ({'Gom mua ròng tích cực' if b_row['Khối ngoại ròng'] > 0 else 'Bán ròng / Đứng ngoài'})
3. Điểm Xếp hạng Đa nhân tố: {b_row['Điểm Tổng Hợp']:.1f}/100 (Nhóm {b_row['Phân Hạng']})
--------------------------------------------------
🎯 CHIẾN LƯỢC HÀNH ĐỘNG: {b_row['Chiến lược']}
• Tỷ trọng khuyến nghị: {b_row['Tỷ trọng khuyến nghị']}
• Vùng giải ngân đề xuất: {b_p_last*0.995:,.0f} - {b_p_last:,.0f} VNĐ
• Mục tiêu ngắn hạn (Target): {b_target:,.0f} VNĐ (+{(b_target/b_p_last - 1)*100:.1f}%)
• Ngưỡng chặn lỗ kỷ luật (Stop-Loss): {b_stop:,.0f} VNĐ (-{(1 - b_stop/b_p_last)*100:.1f}%)
--------------------------------------------------
💡 Thuyết minh: {b_row['Tín hiệu phân tích']}
(Nguồn: Hệ thống FinTech Smart Screener UEL | VPBankS & SSI FastConnect Data)"""

    st.text_area("📄 Nội dung Bản tin Khuyến nghị (Sao chép và gửi ngay cho khách hàng):", flash_note_content, height=310)
    st.info("💡 Môi giới chỉ cần bấm vào ô trên, nhấn `Ctrl + A` và `Ctrl + C` để gửi ngay cho các nhóm nhà đầu tư của mình.")

# TAB 5: PHƯƠNG PHÁP LUẬN & MIỄN TRỪ
with tab_method:
    st.markdown("""
    ### 📐 Kiến trúc Đa nguồn & Cơ sở Khoa học Tài chính

    Hệ thống được thiết kế theo mô hình **Sản phẩm FinTech Hỗ trợ Quyết định Đầu tư**:
    - **Không dừng lại ở việc hiển thị bảng giá đơn thuần**, hệ thống chuyển hóa dữ liệu sổ lệnh thô thành **Chiến lược Hành động Cụ thể** và **Khung Quản trị Vị thế/Rủi ro** cho từng nhà đầu tư.
    - **Cổng chính VPBankS NeoAPI:** Tuân thủ chuẩn JWT Bearer và IP Whitelist `14.187.239.157`.
    - **Cổng bổ sung SSI FastConnect API v3:** Tự động điều phối khi môi trường máy trạm nằm ngoài dải IP đã đăng ký, bảo đảm **100% dữ liệu thị trường thực tế** (HOSE / VN30).

    #### Các trụ cột định lượng vi cấu trúc:
    1. **Độ lệch Cung - Cầu Sổ lệnh (Order Book Imbalance - OBI):**
       $$OBI = \\frac{\\sum_{i=1}^3 \\text{BidVol}_i - \\sum_{i=1}^3 \\text{AskVol}_i}{\\sum_{i=1}^3 \\text{BidVol}_i + \\sum_{i=1}^3 \\text{AskVol}_i} \\in [-1.0, 1.0]$$
    
    2. **Thanh khoản & Giá trị Giao dịch:** Xếp hạng theo phân vị của `totalTradingValue` nhằm lọc các mã có thanh khoản thật và dòng tiền hoạt động mạnh.
    
    3. **Dòng tiền Nước ngoài (Foreign Flow Impact):**
       $$\\text{Foreign Impact} = \\frac{\\text{Foreign Net Value}}{\\text{Total Traded Value}}$$

    4. **Động lượng phiên (Price Momentum):** Kết hợp tỷ lệ thay đổi giá trong phiên (`percentPriceChange`) và vị thế giá đóng cửa trong biên độ `lowPrice–highPrice`.
    
    5. **Điểm tổng hợp Đa nhân tố (Composite Multi-Factor Score):**
       $$\\text{Score} = 0.30 \\cdot S_{\\text{Momentum}} + 0.25 \\cdot S_{\\text{Liquidity}} + 0.25 \\cdot S_{\\text{Foreign}} + 0.20 \\cdot S_{\\text{OBI}}$$
    
    ---
    
    ### ⚠️ Khuyến cáo Rủi ro & Miễn trừ Trách nhiệm Học thuật
    - **Mục đích đồ án:** Đây là sản phẩm nghiên cứu ứng dụng công nghệ tài chính phục vụ học phần *Gói phần mềm ứng dụng cho tài chính 1* tại Trường Đại học Kinh tế - Luật (UEL).
    - **Không phải khuyến nghị đầu tư:** Mọi dữ liệu, phân tích, xếp hạng và tín hiệu trên bảng điều khiển chỉ mang tính chất tham khảo học thuật, không cấu thành bất kỳ lời chào mua/bán hay tư vấn đầu tư tài chính tiền thật nào.
    """)
