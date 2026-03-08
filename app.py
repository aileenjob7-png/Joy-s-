import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
from utils.scraper import fetch_news_data
from utils.ai import get_ai_summary
from components.ui_cards import apply_custom_css, render_news_card, render_news_list_item
from components.ui_charts import (
    render_search_trend_area_chart,
    render_gender_distribution_donut, render_device_distribution,
    render_age_search_ratio_bar,
    render_keyword_radar_chart, get_seasonality_text,
    render_keyword_summary_card
)
from utils.cache import load_weekly_cache, save_weekly_cache
from datetime import datetime

# ─── 페이지 설정 ───────────────────────────────────────
st.set_page_config(
    page_title="마더스올 브랜딩 스터디",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()


# ─── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:24px 20px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px;'>
        <div style='font-size:27px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;'>🧬 마더스올</div>
        <div style='font-size:12px; color:rgba(255,255,255,0.5); margin-top:6px;'>브랜딩 스터디 대시보드</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "nav",
        ["📚  브랜딩 스터디", "🔬  유산균 시장 포커스", "📊  마케팅 데이터랩"],
        label_visibility="collapsed"
    )

    # 콘텐츠와 푸터 겹침 방지용 강제 여백
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

    # 최하단 고정 - flex + mt-auto 효과 (absolute bottom)
    st.markdown(f"""
    <div style='position:absolute; bottom:20px; left:0; right:0; padding:10px 20px 0; background-color:#18213a;'>
        <div style='font-size:11px; color:rgba(255,255,255,0.35);'>{datetime.now().strftime('%Y-%m-%d')}</div>
        <div style='font-size:11px; color:rgba(255,255,255,0.35); margin-top:2px;'>Powered by GPT-4o-mini</div>
    </div>
    """, unsafe_allow_html=True)


# ─── 헬퍼: 페이지 헤더 (업데이트 버튼 포함) ──────────────
def page_header(icon: str, title: str, subtitle: str, show_update_btn: bool = False, btn_key: str = ""):
    """페이지 헤더 + 선택적으로 우상단에 outline 업데이트 버튼을 렌더링합니다."""
    h_col, b_col = st.columns([5.5, 1.2])
    with h_col:
        st.markdown(f"""
        <div style='padding:4px 0 18px;'>
            <h2 style='margin:0; font-size:1.45rem; font-weight:800; color:#0f172a;'>{icon} {title}</h2>
            <p style='margin:5px 0 0; font-size:0.83rem; color:#94a3b8;'>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    if show_update_btn:
        with b_col:
            st.markdown('<div class="btn-outline-update">', unsafe_allow_html=True)
            clicked = st.button("🔄 이번 주 업데이트", key=btn_key, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return clicked
    return False


# ─── 헬퍼: 섹션 패널 감싸기 (흰색 카드) ──────────────────
def panel_start(title="", subtitle=""):
    title_html = f"<h4 style='margin:0 0 2px; font-size:0.88rem; font-weight:700; color:#1e293b;'>{title}</h4>" if title else ""
    sub_html    = f"<p style='margin:0 0 6px; font-size:0.75rem; color:#94a3b8;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""<div style='background:#fff; border-radius:10px; padding:14px 18px;
        border:1px solid #e8ecf0; box-shadow:0 1px 3px rgba(0,0,0,0.03); margin-bottom:10px;'>
        {title_html}{sub_html}""", unsafe_allow_html=True)

def panel_end():
    st.markdown("</div>", unsafe_allow_html=True)


# ─── 뉴스 대시보드 ( 브랜딩/유산균 공용 ) ──────────────────
def display_dashboard(mode: str, update_btn: bool = False, sub_mode: str = "legacy", time_filter: str = ""):
    from utils.cache import get_all_historical_titles, get_history_file_list, load_cache_by_filename
    
    cached_data = load_weekly_cache(mode, sub_mode)
    data_to_render = cached_data

    if update_btn:
        label_kr = "브랜딩 우수 사례" if mode == "study" else "유산균 관련 기사"
        with st.status(f"{label_kr} 탐색 중... 🚀", expanded=True) as status:
            st.write("최신 소식을 스크래핑 중입니다...")
            
            # 중복 방지: 역대 모든 기사 제목 세트 가져오기
            exclude_titles = get_all_historical_titles(mode)
            
            raw_data = fetch_news_data(mode, sample_size=6, exclude_titles=exclude_titles, time_filter=time_filter)
            if not raw_data:
                status.update(label="데이터를 찾을 수 없습니다. 다시 시도해주세요.", state="error", expanded=False)
                return
            st.write(f"{len(raw_data)}개 기사 수집. AI 분석 중...")
            processed, progress_bar = [], st.progress(0)
            for idx, item in enumerate(raw_data):
                summary = get_ai_summary(item['title'], item['snippet'], mode)
                progress_bar.progress((idx + 1) / len(raw_data))
                if summary == "SKIP" or len(summary) < 10:
                    continue
                import re as _re
                
                # 1. AI 응답 내 할루시네이션(HTML 코드 등) 사전에 제거
                # AI가 간혹 footer HTML 등을 생성하는 경우가 있어 모든 태그 제거
                summary = _re.sub(r'<[^>]+>', '', summary).strip()
                
                # 2. [핵심요약 : ...] 태그 추출 (study 모드만, 개행 포함 처리)
                key_summary = ""
                if mode == "study":
                    # 대괄호 안의 내용을 최대한 넓게 탐색
                    ks_match = _re.search(r'\[\s*(핵심요약|핵심 요약)\s*[:：]\s*([\s\S]+?)\s*\]', summary)
                    if ks_match:
                        key_summary = ks_match.group(2).strip()
                        # 본문에서 해당 태그 삭제 (개행 포함)
                        summary = _re.sub(r'\[\s*(핵심요약|핵심 요약)\s*[:：][\s\S]+?\]', '', summary).strip()
                
                item['ai_summary'] = summary
                item['key_summary'] = key_summary
                processed.append(item)
            if processed:
                save_weekly_cache(mode, processed, sub_mode)
            status.update(label=f"완료! {len(processed)}개 인사이트 갱신 🎉", state="complete", expanded=False)
        data_to_render = processed

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    if data_to_render is None:
        st.info("👋 저장된 데이터가 없습니다. 위 버튼을 눌러 가져와 주세요.")
    elif len(data_to_render) == 0:
        st.warning("📍 유효한 뉴스가 부족합니다. 다시 시도해 주세요.")
    else:
        cols = st.columns(2, gap="medium")
        for idx, item in enumerate(data_to_render):
            with cols[idx % 2]:
                render_news_card(item)

    # ─── 히스토리 관리 섹션 (하단) ───
    if mode == "study":
        st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
        panel_start("📅 과거 스터디 다시보기", "이전에 수집했던 주차별 스터디 기사들을 확인할 수 있습니다.")
        
        # 현재 서브모드에 맞는 히스토리만 가져오기
        history_list = get_history_file_list(mode, sub_mode)
        if not history_list:
            st.write("기록된 과거 스터디가 없습니다.")
        else:
            # 주차 선택 셀렉트박스 (sub_mode별 고유 키 부여)
            history_options = [f"{h['year']}년 {h['week']}주차 스터디" for h in history_list]
            selected_idx = st.selectbox("주차 선택", range(len(history_options)), 
                                        format_func=lambda i: history_options[i],
                                        key=f"sb_history_{sub_mode or 'default'}")
            
            if st.button("기록 불러오기", key=f"btn_history_{sub_mode or 'default'}"):
                selected_file = history_list[selected_idx]['filename']
                history_data = load_cache_by_filename(selected_file)
                if history_data:
                    st.success(f"📌 {history_options[selected_idx]} 기록을 불러왔습니다.")
                    st.markdown('<div class="history-list-container">', unsafe_allow_html=True)
                    for h_item in history_data:
                        render_news_list_item(h_item)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("데이터 로드 중 오류가 발생했습니다.")
        panel_end()


# ═══════════════════════════════════════════════════════
# 라우팅 — st.empty()로 각 탭 격리하여 고스팅 방지
# ═══════════════════════════════════════════════════════

# 탭 전환 시 이전 탭 잔상을 없애기 위해 단일 컨테이너에 렌더링
main_area = st.empty()

with main_area.container():
    if menu == "📚  브랜딩 스터디":
        # 현재 주차 계산 (n월 m주차)
        from datetime import date
        import math
        today = date.today()
        first_day = today.replace(day=1)
        # 월의 몇 번째 주인지 계산 (1일의 요일 고려)
        dom = today.day
        adjusted_dom = dom + first_day.weekday()
        week_of_month = int(math.ceil(adjusted_dom / 7.0))
        
        st.markdown(f"""
        <div style='display:inline-flex;align-items:center;gap:10px;margin-bottom:4px;'>
            <span style='background:linear-gradient(135deg,#667eea,#764ba2);color:white;
                font-size:0.78rem;font-weight:700;padding:3px 12px;border-radius:20px;
                letter-spacing:0.3px;'>📅 {today.month}월 {week_of_month}주차 브랜딩 스터디</span>
        </div>
        """, unsafe_allow_html=True)

        tab_latest, tab_legacy = st.tabs(["🚀 (2026~) 최신 브랜딩 스터디", "🏛️ (~2025) 브랜딩 스터디"])
        
        with tab_latest:
            clicked_latest = page_header("🚀", "최신 브랜딩 스터디", "최근 1개월 내에 발행된 새로운 아티클을 수집합니다.",
                                         show_update_btn=True, btn_key="btn_study_latest")
            display_dashboard("study", update_btn=clicked_latest, sub_mode="latest", time_filter="when:30d")

        with tab_legacy:
            clicked_legacy = page_header("🏛️", "기존 브랜딩 스터디", "사이트별 제한 없이 브랜딩 우수 사례를 광범위하게 수집합니다.",
                                         show_update_btn=True, btn_key="btn_study_legacy")
            display_dashboard("study", update_btn=clicked_legacy, sub_mode="legacy")

    elif menu == "🔬  유산균 시장 포커스":
        clicked = page_header("🔬", "유산균 시장 포커스", "프로바이오틱스 시장의 최신 동향과 뉴스를 주간 단위로 파악합니다.",
                               show_update_btn=True, btn_key="btn_probiotics")
        display_dashboard("probiotics", update_btn=clicked)

    elif menu == "📊  마케팅 데이터랩":
        page_header("📊", "마케팅 데이터랩", "네이버 데이터랩 API 실시간 데이터 기반으로 키워드 검색 트렌드를 분석합니다.")

        # ── 키워드 선택기 ──────────────────────────────────────
        kw_col, info_col = st.columns([2.5, 5])
        with kw_col:
            KEYWORDS = ["프로바이오틱스", "유산균", "장건강", "락토바실러스", "비피더스", "유익균"]
            selected_kw = st.selectbox(
                "🔍 분석 키워드 선택", KEYWORDS, index=0,
                key="datalab_kw_select",
                help="키워드를 변경하면 아래 모든 차트가 해당 키워드의 실제 네이버 API 데이터로 업데이트됩니다."
            )
            if st.button("🔄 데이터 새로고침", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with info_col:
            st.markdown(f"""<div style='background:linear-gradient(135deg,#f0f9ff,#e0f2fe); border-radius:10px; padding:12px 16px; margin-top:22px;'>
                <span style='font-size:0.82rem; color:#0369a1;'>📡 데이터는 웹과 동일한 <b>1년 기간/상상대값</b> 기준입니다 (1시간 캐시)</span>
                <div style='font-size:0.7rem; color:#0c4a6e; margin-top:4px;'>※ 네이버 API 특성상 조회 시점/단위에 따라 웹 UI와 미세한 차이가 있을 수 있습니다.</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

        # ── 1. 상단: 레이더 + 요약 (1:1 비율) ─────────────────────
        col_radar, col_summary = st.columns(2, gap="large")
        with col_radar:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #f4a261;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>🎯</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>키워드 종합지수</span>
                    <span style='margin-left:auto;background:#fff7ed;color:#f97316;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #fed7aa;'>5축 평가</span>
                </div>
                <div style='font-size:0.78rem;color:#94a3b8;padding-left:2px;'>
                    '{selected_kw}' 검색트렌드 · 모바일 · 여성비중 · 계절성 · 성장률을 0~100pt로 측정
                </div>
            </div>""", unsafe_allow_html=True)
            render_keyword_radar_chart(selected_kw)
        with col_summary:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #60a5fa;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>📋</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>키워드 요약</span>
                    <span style='margin-left:auto;background:#eff6ff;color:#3b82f6;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #bfdbfe;'>데이터랩 API</span>
                </div>
                <div style='font-size:0.78rem;color:#94a3b8;padding-left:2px;'>
                    '{selected_kw}' 피크 시즌 · 데이터 소스 · 상대값 기준 안내
                </div>
            </div>""", unsafe_allow_html=True)
            seasonality = get_seasonality_text(selected_kw)
            render_keyword_summary_card(selected_kw, seasonality)

        st.markdown("<hr style='border:none; border-top:1.5px solid #e8ecf0; margin:28px 0;'>", unsafe_allow_html=True)

        # ── 2. 트렌드 비교 (검색 vs 쇼핑) ───────────────────────
        col_t1, col_t2 = st.columns(2, gap="large")
        with col_t1:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #22c55e;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>🔍</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>검색 트렌드 (최근 1년)</span>
                    <span style='margin-left:auto;background:#f0fdf4;color:#16a34a;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #bbf7d0;'>정보 탐색</span>
                </div>
                <div style='font-size:0.75rem;color:#94a3b8;padding-left:2px;'>
                    네이버 통합검색어 추이 (0~100pt)
                </div>
            </div>""", unsafe_allow_html=True)
            from components.ui_charts import render_search_trend_area_chart
            render_search_trend_area_chart(keyword=selected_kw)

        with col_t2:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #f43f5e;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>🛒</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>쇼핑 클릭 트렌드 (최근 1년)</span>
                    <span style='margin-left:auto;background:#fff1f2;color:#e11d48;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #fecdd3;'>구매 의향</span>
                </div>
                <div style='font-size:0.75rem;color:#94a3b8;padding-left:2px;'>
                    네이버 쇼핑(건강식품) 클릭 추이 (0~100pt)
                </div>
            </div>""", unsafe_allow_html=True)
            from components.ui_charts import render_shopping_trend_chart
            render_shopping_trend_chart(keyword=selected_kw)

        st.markdown("<hr style='border:none; border-top:1.5px solid #e8ecf0; margin:28px 0;'>", unsafe_allow_html=True)

        # ── 3. 인사이트 상세 분석 ──────────────────────────────
        st.markdown(f"""
        <div style='padding:0 0 16px 0; border-bottom:1px solid #e8ecf0; margin-bottom:20px; text-align: center;'>
            <div style='font-size:1.15rem; font-weight:800; color:#0f172a;'>인사이트 상세 분석 — '{selected_kw}'</div>
            <div style='font-size:0.85rem; color:#64748b; margin-top:4px;'>정보 검색 vs 실제 구매 패턴 비교 (네이버 데이터랩 API 실측 기반)</div>
        </div>
        """, unsafe_allow_html=True)

        # 성별 + 기기별 (1:1 비율)
        g_col1, g_col2 = st.columns(2, gap="large")
        with g_col1:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #f72585;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>👥</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>성별 검색/구매 비중</span>
                    <span style='margin-left:auto;background:#fdf2f8;color:#db2777;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #fbcfe8;'>비교분석</span>
                </div>
                <div style='font-size:0.75rem;color:#94a3b8;padding-left:2px;'>
                    정보 검색 시와 실제 쇼핑 클릭 시의 성별 차이
                </div>
            </div>""", unsafe_allow_html=True)
            render_gender_distribution_donut(selected_kw)
        with g_col2:
            st.markdown(f"""
            <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
                box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
                border-left:4px solid #8b5cf6;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                    <span style='font-size:1.3rem;'>📱</span>
                    <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.3px;'>기기별 접속/쇼핑 비중</span>
                    <span style='margin-left:auto;background:#f5f3ff;color:#7c3aed;
                        font-size:0.7rem;font-weight:700;padding:2px 8px;
                        border-radius:20px;border:1px solid #ddd6fe;'>비교분석</span>
                </div>
                <div style='font-size:0.75rem;color:#94a3b8;padding-left:2px;'>
                    모바일 구매가 압도적인 쇼핑 트렌드 실측 데이터
                </div>
            </div>""", unsafe_allow_html=True)
            render_device_distribution(selected_kw)

        st.markdown("<hr style='border:none; border-top:1.5px solid #e8ecf0; margin:20px 0;'>", unsafe_allow_html=True)

        # 연령별
        st.markdown(f"""
        <div style='background:white;border:1px solid #edf2f7;border-radius:12px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);padding:18px 22px 10px;
            border-left:4px solid #60a5fa;'>
            <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                <span style='font-size:1.3rem;'>📊</span>
                <span style='font-size:1.05rem;font-weight:800;color:#0f172a;
                    letter-spacing:-0.3px;'>연령별 검색 비율</span>
                <span style='margin-left:auto;background:#eff6ff;color:#3b82f6;
                    font-size:0.7rem;font-weight:700;padding:2px 8px;
                    border-radius:20px;border:1px solid #bfdbfe;'>API 실측</span>
            </div>
            <div style='font-size:0.78rem;color:#94a3b8;padding-left:2px;'>
                '{selected_kw}' 10대 ~ 50대+ 연령대별 검색 구성 비율 — 가장 높은 구간이 주요 타겟입니다
            </div>
        </div>""", unsafe_allow_html=True)
        render_age_search_ratio_bar(selected_kw)


