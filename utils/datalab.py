import os
import streamlit as st
import urllib.request
import json
import pandas as pd
from datetime import datetime, timedelta

# ─── 인증 ──────────────────────────────────────────────
def get_datalab_credentials():
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        try:
            client_id = st.secrets["NAVER_CLIENT_ID"]
            client_secret = st.secrets["NAVER_CLIENT_SECRET"]
        except Exception:
            pass
    if client_id: client_id = client_id.strip()
    if client_secret: client_secret = client_secret.strip()
    return client_id, client_secret


def _call_naver_api(url: str, body: dict) -> dict | None:
    """네이버 API 공통 호출 유틸"""
    client_id, client_secret = get_datalab_credentials()
    if not client_id or not client_secret:
        return None
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", str(client_id))
    req.add_header("X-Naver-Client-Secret", str(client_secret))
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, data=json.dumps(body).encode("utf-8"))
        if resp.getcode() == 200:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        st.warning(f"API 호출 오류: {e}")
    return None


def _date_range(days: int = 365):
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ═══════════════════════════════════════════════════════
# 1. 통합검색어 트렌드 — 월별 검색 추이 (상대값 0~100)
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_keyword_trend(keywords: list, time_unit: str = "month") -> pd.DataFrame:
    start, end = _date_range(365)
    body = {
        "startDate": start, "endDate": end, "timeUnit": time_unit,
        "keywordGroups": [{"groupName": kw, "keywords": [kw]} for kw in keywords],
    }
    data = _call_naver_api("https://openapi.naver.com/v1/datalab/search", body)
    if not data:
        return pd.DataFrame()
    rows = []
    for g in data.get("results", []):
        for item in g.get("data", []):
            rows.append({"period": item["period"], "ratio": item["ratio"], "keyword": g["title"]})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.pivot(index="period", columns="keyword", values="ratio").reset_index().fillna(0)


# ═══════════════════════════════════════════════════════
# 통합 도우미: 필터별 평균 비율 산출
# ═══════════════════════════════════════════════════════

def _fetch_and_average_ratios(keyword: str, filter_dict: dict, days: int = 365) -> dict:
    """공통 패턴인 '필터 반복 호출 -> 평균 계산' 로직을 통합합니다.
    기간을 365일로 늘려 네이버 데이터랩 웹 UI 결과와 수치를 최대한 맞춥니다.
    """
    start, end = _date_range(days)
    base_body = {
        "startDate": start, "endDate": end, "timeUnit": "month",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
    }
    averages = {}
    for key, codes in filter_dict.items():
        body = {**base_body}
        if isinstance(codes, list):
            body["ages"] = codes
        elif key == "female" or key == "male":
            body["gender"] = codes
        elif key == "mobile" or key == "pc":
            body["device"] = codes
            
        data = _call_naver_api("https://openapi.naver.com/v1/datalab/search", body)
        if data and data.get("results") and data["results"][0].get("data"):
            vals = [d["ratio"] for d in data["results"][0].get("data")]
            averages[key] = sum(vals) / max(len(vals), 1)
        else:
            averages[key] = 0
    return averages


# ═══════════════════════════════════════════════════════
# 2. 검색 트렌드 — 성별 비율
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_gender_ratio(keyword: str) -> dict:
    """{'female_pct': float, 'male_pct': float} 반환"""
    results = _fetch_and_average_ratios(keyword, {"female": "f", "male": "m"}, days=365)
    total = sum(results.values())
    if total == 0:
        return {"female_pct": 50, "male_pct": 50}
    return {
        "female_pct": round(results["female"] / total * 100, 1),
        "male_pct": round(results["male"] / total * 100, 1),
    }


# ═══════════════════════════════════════════════════════
# 3. 검색 트렌드 — 기기별 (PC vs 모바일)
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_device_ratio(keyword: str) -> dict:
    """{'mobile_pct': float, 'pc_pct': float} 반환"""
    results = _fetch_and_average_ratios(keyword, {"mobile": "mo", "pc": "pc"})
    total = sum(results.values())
    if total == 0:
        return {"mobile_pct": 50, "pc_pct": 50}
    return {
        "mobile_pct": round(results["mobile"] / total * 100, 1),
        "pc_pct": round(results["pc"] / total * 100, 1),
    }


# ═══════════════════════════════════════════════════════
# 4. 검색 트렌드 — 연령별
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_age_ratio(keyword: str) -> dict:
    """{'10대': float, '20대': float, '30대': float, '40대': float, '50대이상': float}"""
    age_groups = {
        "10대": ["2"], "20대": ["3", "4"], "30대": ["5", "6"],
        "40대": ["7", "8"], "50대이상": ["9", "10", "11"],
    }
    results = _fetch_and_average_ratios(keyword, age_groups)
    total = sum(results.values())
    if total == 0:
        return {k: 20 for k in age_groups}
    return {k: round(v / total * 100, 1) for k, v in results.items()}


# ═══════════════════════════════════════════════════════
# 5. 월별 트렌드 (검색 트렌드 차트용) — 상대값 시계열
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_monthly_trend(keyword: str) -> pd.DataFrame:
    """period(날짜)와 ratio(0~100) 컬럼의 DataFrame 반환"""
    start, end = _date_range(365)
    body = {
        "startDate": start, "endDate": end, "timeUnit": "month",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
    }
    data = _call_naver_api("https://openapi.naver.com/v1/datalab/search", body)
    if not data or not data.get("results"):
        return pd.DataFrame()
    rows = [{"period": d["period"], "ratio": d["ratio"]}
            for d in data["results"][0].get("data", [])]
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════
# 6. 레이더 차트용 — 5축 지표 (여러 필터 조합 호출)
# ═══════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_radar_metrics(keyword: str) -> dict:
    """
    5가지 축: 검색트렌드(최근 3개월 평균), 모바일비중, 여성비중, 계절변동성, 최근성장률
    모두 실제 API 호출 기반으로 산출합니다.
    """
    # 월별 트렌드
    trend_df = fetch_monthly_trend(keyword)
    if trend_df.empty:
        return {"검색트렌드": 0, "모바일비중": 0, "여성비중": 0, "계절변동성": 0, "최근성장률": 0}

    ratios = trend_df["ratio"].tolist()

    # 최근 3개월 평균 (검색트렌드)
    recent_avg = sum(ratios[-3:]) / max(len(ratios[-3:]), 1)

    # 계절 변동성 (표준편차 기반, 높을수록 계절성 강함)
    std_val = float(pd.Series(ratios).std()) if len(ratios) > 1 else 0
    seasonality = min(std_val * 3, 100)  # 스케일링

    # 최근 성장률 (최근 3개월 vs 이전 3개월)
    if len(ratios) >= 6:
        prev_avg = sum(ratios[-6:-3]) / 3
        growth = ((recent_avg - prev_avg) / max(prev_avg, 1)) * 100
        growth_score = min(max(growth + 50, 0), 100)  # 0~100 범위로
    else:
        growth_score = 50

    # 기기/성별
    device = fetch_device_ratio(keyword)
    gender = fetch_gender_ratio(keyword)

    return {
        "검색트렌드": round(float(recent_avg), 1),
        "모바일비중": round(float(device["mobile_pct"]), 1),
        "여성비중": round(float(gender["female_pct"]), 1),
        "계절변동성": round(float(seasonality), 1),
        "최근성장률": round(float(growth_score), 1),
    }


# ═══════════════════════════════════════════════════════
# 하위 호환용 stub
# ═══════════════════════════════════════════════════════
def fetch_demographic_trend(keyword: str, time_unit: str = "month") -> pd.DataFrame:
    return pd.DataFrame()
