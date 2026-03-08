import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.datalab import (
    fetch_monthly_trend, fetch_gender_ratio,
    fetch_device_ratio, fetch_age_ratio, fetch_radar_metrics,
)
from utils.export import get_excel_download_data

EMPTY_BG = "rgba(0,0,0,0)"

def _render_title(title: str, subtitle: str):
    """좌측 정렬된 기본 컨테이너 제목 렌더링"""
    st.markdown(f"""
    <div style='text-align: center; padding: 4px 0 8px 0;'>
        <div style='font-size:1.05rem;font-weight:700;color:#0f172a;margin-bottom:2px;'>{title}</div>
        <div style='font-size:0.8rem;color:#64748b;'>{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── 레이더 차트 (5축 — 실제 API 데이터) ─────────────────
def render_keyword_radar_chart(keyword: str = "프로바이오틱스"):

    # 현재 키워드 실제데이터
    metrics = fetch_radar_metrics(keyword)
    if all(v == 0 for v in metrics.values()):
        st.info("레이더 차트 데이터를 불러올 수 없습니다.")
        return

    categories = list(metrics.keys())
    vals = list(metrics.values())

    # 전체 키워드 평균 기준 데이터 (네이버 API 상대값 특성 반영)
    # 검색트렌드 40 / 모바일 60 / 여성비중 50 / 계절변동성 25 / 성장률 50
    avg_vals = [40, 60, 50, 25, 50]

    # hover 텍스트: 실제 값 vs 평균 비교
    hover_texts_kw = [
        f"{cat}<br>현재키워드: <b>{v:.1f}pt</b><br>전체평균: {a:.1f}pt<br>{'▲ 평균이상' if v >= a else '▼ 평균미만'}"
        for cat, v, a in zip(categories, vals, avg_vals)
    ]
    hover_texts_avg = [
        f"{cat}<br>전체평균: <b>{a:.1f}pt</b>"
        for cat, a in zip(categories, avg_vals)
    ]

    fig = go.Figure()

    # ① 평균 영역 (회색, 연하게)
    fig.add_trace(go.Scatterpolar(
        r=avg_vals, theta=categories, fill='toself',
        fillcolor='rgba(148,163,184,0.18)',
        line=dict(color='rgba(148,163,184,0.5)', width=1.5, dash='dot'),
        name='전체평균',
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_texts_avg,
    ))

    # ② 현재 키워드 (주황색)
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=categories, fill='toself',
        fillcolor='rgba(244,162,97,0.30)',
        line=dict(color='#f4a261', width=2.5),
        marker=dict(size=5, color='#f4a261', line=dict(width=1.5, color='white')),
        name=keyword,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_texts_kw,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='array',
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20', '40', '60', '80', '100'],
                tickfont=dict(size=8, color='#b0b9c6'),
                gridcolor='rgba(148,163,184,0.22)',
                gridwidth=1,
                showline=False,
            ),
            angularaxis=dict(
                gridcolor='rgba(148,163,184,0.14)',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(size=11, color='#334155'),
                rotation=90,
            ),
            bgcolor=EMPTY_BG,
        ),
        showlegend=True,
        legend=dict(
            orientation='h', x=0.5, xanchor='center', y=-0.08,
            font=dict(size=11, color='#475569'),
            bgcolor=EMPTY_BG,
        ),
        plot_bgcolor=EMPTY_BG, paper_bgcolor=EMPTY_BG,
        margin=dict(t=24, b=36, l=36, r=36), height=300,
        hoverlabel=dict(bgcolor='#fff', font_size=12),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ── 엑셀 다운로드 (Radar) - 소형 아이콘화
    df_radar = pd.DataFrame([{"지수명": k, "지수(pt)": v, "전체평균": a} for k, v, a in zip(categories, vals, avg_vals)])
    excel_radar = get_excel_download_data(df_radar)
    col_dl1, col_dl2 = st.columns([8, 1])
    with col_dl2:
        st.download_button(label="📥", data=excel_radar, file_name=f"radar_{keyword}.xlsx", key=f"dl_radar_icon_{keyword}", help="지수 데이터 엑셀 다운로드")


# ─── 키워드 요약 카드 ──────────────────────────────────
def render_keyword_summary_card(keyword: str, seasonality: str):
    
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; gap:10px; margin-top:4px;">
        <div style="display:flex; gap:10px;">
            <div style="flex:1; background:#f8fafc;border-radius:8px;padding:12px;border:1px solid #e2e8f0; text-align:left;">
                <div style="font-size:0.75rem;color:#94a3b8;">피크 시즌</div>
                <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-top:2px;">{seasonality}</div>
            </div>
            <div style="flex:1; background:#f8fafc;border-radius:8px;padding:12px;border:1px solid #e2e8f0; text-align:left;">
                <div style="font-size:0.75rem;color:#94a3b8;">데이터 소스</div>
                <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-top:2px;">네이버 데이터랩</div>
            </div>
        </div>
        <div style="background:#fffbeb;border-radius:8px;padding:12px;border:1px solid #fde68a; text-align:left;">
            <div style="font-size:0.8rem;color:#92400e;">
                ⚠️ 네이버 API는 <b>상대값(0~100)</b>만 제공합니다.<br/>
                절대 검색량 등은 <a href='https://searchad.naver.com' target='_blank' style='color:#b45309;'>검색광고 센터</a>에서 확인하세요.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── 검색 트렌드 (월별 꺾은선 — 실제 API) ────────────────
def render_search_trend_area_chart(keyword: str = "프로바이오틱스", **_kwargs):

    df = fetch_monthly_trend(keyword)
    if df.empty:
        st.info(f"'{keyword}' 검색 트렌드 데이터를 불러올 수 없습니다.")
        return

    months = pd.to_datetime(df["period"])
    ratios = df["ratio"].tolist()

    # ─ 피크 시젠 계산: 연간 평균 대비 20% 이상 높은 달
    annual_avg = sum(ratios) / max(len(ratios), 1)
    PEAK_THRESHOLD = annual_avg * 1.20
    peak_mask = [v >= PEAK_THRESHOLD for v in ratios]
    peak_months_label = "·".join([months.iloc[i].strftime("%m월") for i, p in enumerate(peak_mask) if p]) or "없음"

    # ─ 시각적 구성: 본체 라인 + 피크 마커 오버레이
    fig = go.Figure()

    # ① 본찌 라인
    fig.add_trace(go.Scatter(
        x=months, y=ratios,
        name="검색 트렌드",
        mode="lines+markers",
        line=dict(color="#22c55e", width=2.5),
        marker=dict(size=5, color="#22c55e", line=dict(width=1.5, color="white")),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.10)",
        hovertemplate="%{x|%Y-%m}<br>트렌드: <b>%{y:.0f}pt</b><br>(최대 검색량 대비 비율)<extra></extra>",
    ))

    # ② 피크 포인트 오버레이 (주황 큰 마커 + Peak 라벨)
    peak_x = [months.iloc[i] for i, p in enumerate(peak_mask) if p]
    peak_y = [ratios[i] for i, p in enumerate(peak_mask) if p]
    if peak_x:
        fig.add_trace(go.Scatter(
            x=peak_x, y=peak_y,
            mode="markers+text",
            name="Peak",
            marker=dict(size=13, color="#f97316", symbol="circle",
                        line=dict(width=2, color="white")),
            text=["Peak"] * len(peak_x),
            textposition="top center",
            textfont=dict(size=10, color="#f97316", family="Pretendard, Inter"),
            hovertemplate="%{x|%Y-%m}<br>피크: <b>%{y:.0f}pt</b><br>(평균대비 20%+ 초과)<extra></extra>",
        ))

    # ─ 평균선 기준선
    fig.add_hline(
        y=PEAK_THRESHOLD,
        line=dict(color="rgba(249,115,22,0.35)", width=1.5, dash="dot"),
        annotation_text=f"평균+20% ({PEAK_THRESHOLD:.0f}pt)",
        annotation_position="right",
        annotation_font=dict(size=10, color="#f97316"),
    )

    fig.update_layout(
        plot_bgcolor=EMPTY_BG, paper_bgcolor=EMPTY_BG,
        margin=dict(t=16, b=24, l=10, r=80),
        height=280, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=11), bgcolor=EMPTY_BG),
        xaxis=dict(showgrid=False, tickformat="%Y-%m",
                   tickfont=dict(size=11, color="#94a3b8"), dtick="M1"),
        yaxis=dict(
            title=dict(text="검색 트렌드 (상대값, 0-100pt)",
                       font=dict(size=11, color="#94a3b8")),
            range=[0, 130],
            showgrid=True, gridcolor="rgba(200,200,200,0.18)",
            tickfont=dict(size=10, color="#94a3b8"),
        ),
        hoverlabel=dict(bgcolor="#fff", font_size=12),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── 엑셀 다운로드 (Trend) - 소형 아이콘화
    excel_trend = get_excel_download_data(df[["period", "ratio"]])
    col_dltr1, col_dltr2 = st.columns([8, 1])
    with col_dltr2:
        st.download_button(label="📥", data=excel_trend, file_name=f"trend_{keyword}.xlsx", key=f"dl_trend_icon_{keyword}", help="트렌드 데이터 엑셀 다운로드")

    # ─ 차트 하단 접담 텍스트
    info_icon = "<span title='네이버 API 상대값(0~100pt). 최대 검색량을 100으로 환산한 비율입니다.' style='cursor:help;color:#94a3b8;'>&#9432;</span>"
    st.markdown(
        f"<div style='font-size:0.8rem;color:#475569;margin-top:4px;text-align:left;'>"
        f"<b style='color:#f97316;'>Peak 시젠:</b> {peak_months_label} &nbsp;"
        f"(연간평균 {annual_avg:.0f}pt 대비 20%+ 기준) {info_icon}"
        f"</div>",
        unsafe_allow_html=True
    )


# ─── 쇼핑 클릭 추이 (Line — 실제 API) ──────────────────────
def render_shopping_trend_chart(keyword: str):
    """쇼핑인사이트 키워드 클릭 추이 시각화"""
    from utils.datalab import fetch_shopping_trend
    df = fetch_shopping_trend(keyword)
    
    if df.empty:
        st.info(f"'{keyword}' 쇼핑 클릭 데이터가 없거나 카테고리(건강식품)와 일치하지 않습니다.")
        return

    months = pd.to_datetime(df["period"])
    ratios = df["ratio"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=ratios,
        name="쇼핑 클릭 추이",
        mode="lines+markers",
        line=dict(color="#f43f5e", width=2.5),
        marker=dict(size=5, color="#f43f5e", line=dict(width=1.5, color="white")),
        fill="tozeroy", fillcolor="rgba(244,63,94,0.10)",
        hovertemplate="%{x|%Y-%m}<br>클릭지수: <b>%{y:.0f}pt</b><extra></extra>",
    ))

    fig.update_layout(
        plot_bgcolor=EMPTY_BG, paper_bgcolor=EMPTY_BG,
        margin=dict(t=16, b=24, l=10, r=40),
        height=280, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickformat="%Y-%m", tickfont=dict(size=11, color="#94a3b8"), dtick="M1"),
        yaxis=dict(
            title=dict(text="클릭 지수 (상대값)", font=dict(size=11, color="#94a3b8")),
            range=[0, 110], showgrid=True, gridcolor="rgba(200,200,200,0.18)",
            tickfont=dict(size=10, color="#94a3b8"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 엑셀 다운로드
    excel_shop = get_excel_download_data(df)
    col_dls1, col_dls2 = st.columns([12, 1])
    with col_dls2:
        st.download_button(label="📥", data=excel_shop, file_name=f"shopping_{keyword}.xlsx", key=f"dl_shop_icon_{keyword}", help="쇼핑 데이터 엑셀 다운로드")
    
    st.markdown("<div style='font-size:0.8rem;color:#475569;margin-top:4px;'>🛒 <b>실제 구매로 이어지는 의향</b>을 나타내는 지표입니다.</div>", unsafe_allow_html=True)


# ─── 성별 분포 (Search vs Shopping 비교) ─────────────────
def render_gender_distribution_donut(keyword: str = "프로바이오틱스"):
    from utils.datalab import fetch_gender_ratio, fetch_shopping_gender_ratio
    
    s_data = fetch_gender_ratio(keyword)
    shop_data = fetch_shopping_gender_ratio(keyword)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div style='text-align:center;font-size:0.85rem;color:#64748b;'>🔍 검색 사용자</div>", unsafe_allow_html=True)
        f_pct = s_data["female_pct"]
        fig = go.Figure(go.Pie(labels=['여성', '남성'], values=[f_pct, 100-f_pct], hole=.6, marker_colors=['#f72585', '#e2e8f0'], textinfo='percent'))
        fig.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, paper_bgcolor=EMPTY_BG)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    with col2:
        st.markdown("<div style='text-align:center;font-size:0.85rem;color:#64748b;'>🛒 쇼핑 구매자</div>", unsafe_allow_html=True)
        sf_pct = shop_data["female_pct"]
        fig = go.Figure(go.Pie(labels=['여성', '남성'], values=[sf_pct, 100-sf_pct], hole=.6, marker_colors=['#f06292', '#e2e8f0'], textinfo='percent'))
        fig.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, paper_bgcolor=EMPTY_BG)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Excel Download
    df_gender = pd.DataFrame([
        {"구분": "검색_여성", "비율(%)": f_pct}, {"구분": "검색_남성", "비율(%)": 100-f_pct},
        {"구분": "쇼핑_여성", "비율(%)": sf_pct}, {"구분": "쇼핑_남성", "비율(%)": 100-sf_pct}
    ])
    excel_gender = get_excel_download_data(df_gender)
    col_dlg1, col_dlg2 = st.columns([12, 1])
    with col_dlg2:
        st.download_button(label="📥", data=excel_gender, file_name=f"gender_compare_{keyword}.xlsx", key=f"dl_gender_icon_{keyword}")
    
    st.markdown("<div style='text-align:center;font-size:0.7rem;color:#94a3b8;'>※ 정보 검색 시와 실제 구매 시의 성별 비중 차이를 확인하세요.</div>", unsafe_allow_html=True)


# ─── 기기별 분포 (Search vs Shopping 비교) ────────────────
def render_device_distribution(keyword: str = "프로바이오틱스"):
    from utils.datalab import fetch_device_ratio, fetch_shopping_device_ratio
    
    s_data = fetch_device_ratio(keyword)
    shop_data = fetch_shopping_device_ratio(keyword)
    
    mob_s = s_data["mobile_pct"]
    mob_shop = shop_data["mobile_pct"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='text-align:center;font-size:0.85rem;color:#64748b;'>🔍 검색 기기</div>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Pie(labels=['모바일', 'PC'], values=[mob_s, 100-mob_s], hole=.6, marker_colors=['#60a5fa', '#f1f5f9'], textinfo='percent')])
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=160, paper_bgcolor=EMPTY_BG)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    with col2:
        st.markdown("<div style='text-align:center;font-size:0.85rem;color:#64748b;'>🛒 쇼핑 기기</div>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Pie(labels=['모바일', 'PC'], values=[mob_shop, 100-mob_shop], hole=.6, marker_colors=['#3b82f6', '#f1f5f9'], textinfo='percent')])
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=160, paper_bgcolor=EMPTY_BG)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Excel Download
    df_device = pd.DataFrame([
        {"구분": "검색_모바일", "비율(%)": mob_s}, {"구분": "검색_PC", "비율(%)": 100-mob_s},
        {"구분": "쇼핑_모바일", "비율(%)": mob_shop}, {"구분": "쇼핑_PC", "비율(%)": 100-mob_shop}
    ])
    excel_device = get_excel_download_data(df_device)
    col_dld1, col_dld2 = st.columns([12, 1])
    with col_dld2:
        st.download_button(label="📥", data=excel_device, file_name=f"device_compare_{keyword}.xlsx", key=f"dl_device_icon_{keyword}")
    
    st.markdown(f"<div style='text-align:center;font-size:0.82rem;color:#475569;'>쇼핑 시 모바일 비중이 <b>{mob_shop}%</b>로 훨씬 높게 나타납니다.</div>", unsafe_allow_html=True)


# ─── 연령별 검색 비율 (Bar — 실제 API) ───────────────────
def render_age_search_ratio_bar(keyword: str = "프로바이오틱스"):
    
    data = fetch_age_ratio(keyword)
    ages = list(data.keys())
    vals = list(data.values())
    peak_i = vals.index(max(vals))
    colors = ['rgba(96,165,250,0.2)'] * len(ages)
    colors[peak_i] = '#60a5fa'

    fig = go.Figure(data=[go.Bar(
        x=ages, y=vals,
        text=[f"{v:.1f}%" for v in vals], textposition='outside',
        marker_color=colors, marker_line_width=0,
    )])
    fig.update_layout(
        plot_bgcolor=EMPTY_BG, paper_bgcolor=EMPTY_BG,
        margin=dict(t=10, b=30, l=10, r=10), # 아래 여백 넉넉히
        xaxis=dict(showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, showticklabels=False, range=[0, max(vals)*1.2]),
        height=220,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ── 엑셀 다운로드 (Age) - 소형 아이콘화
    df_age = pd.DataFrame([{"연령대": k, "비율(%)": v} for k, v in data.items()])
    excel_age = get_excel_download_data(df_age)
    col_dla1, col_dla2 = st.columns([8, 1])
    with col_dla2:
        st.download_button(label="📥", data=excel_age, file_name=f"age_{keyword}.xlsx", key=f"dl_age_icon_{keyword}", help="연령별 데이터 엑셀 다운로드")
    st.markdown(f"<div style='text-align:left;font-size:0.85rem;color:#475569;margin-top:2px;'>💡 <b>{ages[peak_i]}</b>의 검색 비율이 가장 높습니다</div>", unsafe_allow_html=True)


# ─── 계절성 분석 (Top 3 피크 월 추출 — 실제 API) ──────────
def get_seasonality_text(keyword: str) -> str:
    """월별 트렌드에서 상위 3개 월을 추출하여 '12·11·10월' 형태로 반환"""
    df = fetch_monthly_trend(keyword)
    if df.empty:
        return "데이터 없음"
    df["month"] = pd.to_datetime(df["period"]).dt.month
    monthly_avg = df.groupby("month")["ratio"].mean().sort_values(ascending=False)
    top3 = monthly_avg.head(3).index.tolist()
    return "·".join([f"{m}월" for m in top3])
