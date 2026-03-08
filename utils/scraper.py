import requests
from bs4 import BeautifulSoup
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def _fetch_rss(url: str, timeout: int = 8) -> list:
    """Google News RSS URL에서 item 리스트를 반환합니다."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, features="xml")
        return soup.findAll('item') or []
    except Exception as e:
        print(f"RSS fetch error: {e}")
        return []

def _parse_items(items, mode: str, seen_titles: set, limit: int) -> list:
    """RSS item 리스트를 파싱해 뉴스 dict 리스트로 변환합니다."""
    results = []
    for i in items:
        if len(results) >= limit:
            break
        raw_title = i.title.text.split(" - ")[0].strip()
        if raw_title in seen_titles:
            continue
        if mode == "probiotics" and not any(
            kw in raw_title for kw in ["유산균", "프로바이오틱스", "바이옴", "균주", "마이크로"]
        ):
            continue
        pub_date = i.pubDate.text if i.pubDate else "최근"
        snippet_text = ""
        if i.description:
            desc_soup = BeautifulSoup(i.description.text, "html.parser")
            snippet_text = desc_soup.get_text().strip()[:297]
        results.append({
            "title": raw_title,
            "link": i.link.text if i.link else "#",
            "source": i.source.text if i.source else "Industry News",
            "snippet": snippet_text,
            "date": pub_date[5:16] if (pub_date and len(pub_date) > 16) else "최근",
        })
        seen_titles.add(raw_title)
    return results


def fetch_news_data(mode: str, sample_size: int = 6, exclude_titles: set = None, time_filter: str = "") -> list:
    """뉴스를 스크래핑하여 리스트를 반환합니다.
    - study 모드: 3개 소스 그룹에서 각 2개씩 균등 추출 (총 6개)
    - probiotics 모드: 단일 RSS 쿼리에서 sample_size개 추출
    - time_filter: 예) "when:30d" (최근 1개월)
    """
    if mode == "study":
        source_groups = [
            ["longblack.co", "folin.co"],
            ["careet.net", "bemyb.kr"],
            ["openads.co.kr", "mzworld.kr"],
        ]
        keyword = "브랜딩" # 키워드는 단순하게 유지하여 수집 가능성 확보
        per_group = max(1, sample_size // len(source_groups))

        query_suffix = f" {time_filter}" if time_filter else ""
        results, seen = [], (exclude_titles.copy() if exclude_titles else set())
        for group in source_groups:
            site_q = " OR ".join(f"site:{s}" for s in group)
            url = f"https://news.google.com/rss/search?q={keyword} ({site_q}){query_suffix}&hl=ko&gl=KR&ceid=KR:ko"
            items = _fetch_rss(url)
            
            # 특정 그룹 검색 실패 시 해당 그룹 내 사이트 개별 검색 시도
            if not items:
                url_fb = f"https://news.google.com/rss/search?q={keyword} {group[0]}{query_suffix}&hl=ko&gl=KR&ceid=KR:ko"
                items = _fetch_rss(url_fb)
            
            random.shuffle(items)
            parsed = _parse_items(items, mode, seen, per_group)
            results.extend(parsed)

        random.shuffle(results)
        return results[:sample_size]

    else:
        # 유산균 모드 — 기존 방식 유지
        sites = ["hankyung.com", "mk.co.kr", "foodnews.co.kr",
                 "donga.com", "chosun.com", "rapportian.com", "medipana.com"]
        keyword = "(intitle:유산균 OR intitle:프로바이오틱스) (출시 OR 특허 OR 연구 OR 마케팅)"
        site_q = " OR ".join(f"site:{s}" for s in sites)
        url = f"https://news.google.com/rss/search?q={keyword} ({site_q})&hl=ko&gl=KR&ceid=KR:ko"
        items = _fetch_rss(url)
        seen = set()
        results = _parse_items(items, mode, seen, len(items))
        if len(results) >= sample_size:
            return random.sample(results, sample_size)
        random.shuffle(results)
        return results

