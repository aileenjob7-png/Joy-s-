import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ─── 전체 폰트 & 색상 초기화 ─── */
    html, body, [class*="css"],
    .stMarkdown, .stText, p, span {
        font-family: 'Pretendard', 'Inter', -apple-system, sans-serif !important;
    }

    /* ─── 앱 배경 ─── */
    [data-testid="stAppViewContainer"] > .main {
        background-color: #f0f2f5;
    }

    /* ─── 콘텐츠 패딩 ─── */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }

    /* ─── Streamlit 기본 불필요 요소 제거 (단, 사이드바 버튼 보존을 위해 header는 노출) ─── */
    footer,
    [data-testid="stStatusWidget"],
    .stDeployButton { display: none !important; }

    /* ─── 타이포그래피 ─── */
    h1 { font-size: 1.7rem !important; font-weight: 800 !important; color: #0f172a !important; }
    h2 { font-size: 1.4rem !important; font-weight: 800 !important; color: #0f172a !important; }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; color: #1e293b !important; }
    h4 { font-size: 0.95rem !important; font-weight: 700 !important; color: #334155 !important; }

    /* ══════════════════════════════════════
       사이드바 — 라이트 블루-그레이 배경
    ══════════════════════════════════════ */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(160deg, #c8dce8 0%, #d6e8f4 50%, #cde0ee 100%) !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * { color: #2d4a6a !important; }
    /* 사이드바 타먼 다크 데이크 테마 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: #18213a !important;
        border-right: none !important;
        position: relative !important;
        height: 100% !important;
    }
    [data-testid="stSidebar"] * { color: #8b9ab4 !important; }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 10px 0 !important;
    }

    /* 라디오 그룹 박스/스타일 완전 제거 */
    [data-testid="stSidebar"] [data-testid="stRadio"],
    [data-testid="stSidebar"] [data-testid="stRadio"] > div,
    [data-testid="stSidebar"] div[role="radiogroup"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        gap: 0 !important;
        padding: 4px 0 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }

    /* 메뉴 아이템 - 40px 높이의 바 */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        height: 40px !important;
        padding: 0 16px 0 17px !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        border-left: 3px solid transparent !important;
        transition: background 0.15s;
        cursor: pointer;
        overflow: hidden !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        font-size: 17px !important;
        font-weight: 500 !important;
        color: #8b9ab4 !important;
        margin: 0 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        line-height: 40px !important;
    }

    /* 활성 메뉴 */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(255,255,255,0.1) !important;
        border-left: 3px solid #60a5fa !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ══════════════════════════════════════
       뉴스 카드
    ══════════════════════════════════════ */
    .news-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e8ecf0;
        margin-bottom: 16px;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .news-card:hover {
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        border-color: rgba(249,115,22,0.2);
    }
    .news-tag {
        display: inline-block;
        color: #f97316;
        background: #fff7ed;
        padding: 3px 10px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
    }
    .news-title {
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.5;
        margin-bottom: 10px;
        color: #0f172a;
    }
    .news-body {
        font-size: 0.875rem;
        line-height: 1.7;
        flex-grow: 1;
        color: #475569;
        word-break: keep-all;
    }
    .news-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
    }
    .news-date { color: #94a3b8; font-size: 0.78rem; }
    .news-link {
        font-size: 0.8rem;
        font-weight: 600;
        color: #f97316;
        text-decoration: none;
        transition: color 0.2s;
    }
    .news-link:hover { color: #ea580c; text-decoration: none; }

    /* ══════════════════════════════════════
       KPI 카드
    ══════════════════════════════════════ */
    .kpi-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 18px 18px;
        border: 1px solid #e8ecf0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 10px;
        min-height: 88px;
        position: relative;
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 6px;
        letter-spacing: 0.2px;
    }
    .kpi-value {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 800;
        line-height: 1.2;
    }

    /* ══════════════════════════════════════
       섹션 카드 (흰색 패널)
    ══════════════════════════════════════ */
    .section-panel {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e8ecf0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }

    /* ══════════════════════════════════════
       Streamlit 기본 흰 박스 제거
    ══════════════════════════════════════ */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Streamlit 기본 버튼 — 오렌지 primary */
    .stButton > button {
        background: #f97316 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: background 0.15s !important;
    }
    .stButton > button:hover {
        background: #ea580c !important;
    }

    /* ══════════════════════════════════════
       대시보드 전용 카드 (가운데 정렬)
    ══════════════════════════════════════ */
    .dashboard-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e8ecf0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 8px;
    }
    .dashboard-card-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        text-align: center;
    }
    .dashboard-card-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 12px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


def render_news_card(item: dict):
    import html as _html
    # 텍스트 필드는 HTML 이스케이프 처리 (특수문자로 HTML 깨짐 방지)
    safe_title  = _html.escape(item.get('title', ''))
    safe_source = _html.escape(item.get('source', '뉴스'))
    safe_date   = _html.escape(item.get('date', ''))
    safe_link   = item.get('link', '#').replace('"', '%22').strip()
    # ai_summary: HTML 이스케이프 후 <br> 태그만 복구 (GPT의 꺾쇠 출력으로 HTML 깨짐 방지)
    # 또한 백틱(`)이 포함되면 st.markdown이 코드 블록으로 오해하여 레이아웃이 깨지므로 제거
    raw_summary = item.get('ai_summary', '').replace('`', '')
    ai_summary  = _html.escape(raw_summary).replace('&lt;br&gt;', '<br>')
    key_summary = _html.escape(item.get('key_summary', '').strip())

    key_box = f"""
    <div style='background:linear-gradient(135deg,#f0f9ff,#e0f2fe);
        border-left:3px solid #0ea5e9;border-radius:6px;
        padding:8px 12px;margin-top:12px;'>
        <span style='font-size:0.78rem;font-weight:700;color:#0369a1;'>💡 핵심 요약&nbsp;</span>
        <span style='font-size:0.78rem;color:#0c4a6e;'>{key_summary}</span>
    </div>""" if key_summary else ""

    st.markdown(f"""
    <div class="news-card">
        <div><span class="news-tag">{safe_source}</span></div>
        <div class="news-title">{safe_title}</div>
        <div class="news-body">{ai_summary}</div>
        {key_box}
        <div class="news-footer">
            <span class="news-date">{safe_date}</span>
            <a href="{safe_link}" target="_blank" class="news-link">원문 기사 ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)





def render_kpi_card(title: str, value: str, tooltip: str = ""):
    info_svg = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/></svg>'''
    st.markdown(f"""
    <div class="kpi-card" title="{tooltip}">
        <div style="position:absolute; top:10px; right:10px; cursor:help;" title="{tooltip}">{info_svg}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
