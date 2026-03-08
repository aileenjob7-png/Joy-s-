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


def fetch_news_data(mode: str, sample_size: int = 6) -> list:
    """뉴스를 스크래핑하여 리스트를 반환합니다.
    - study 모드: 3개 소스 그룹에서 각 2개씩 균등 추출 (총 6개)
    - probiotics 모드: 단일 RSS 쿼리에서 sample_size개 추출
    """
    if mode == "study":
        # 3그룹 × 2개 = 6개 균등 추출
        source_groups = [
            ["longblack.co", "folin.co", "brunch.co.kr", "careerly.co.kr"], # 소스 추가
            ["careet.net", "bemyb.kr", "openads.co.kr", "publy.co"],
            ["mobiinside.co.kr", "mzworld.kr", "ditoday.com", "bloter.net"],
        ]
        keyword = "브랜드" # 더 넓은 키워드로 변경
        per_group = max(1, sample_size // len(source_groups))

        results, seen = [], set()
        for group in source_groups:
            site_q = " OR ".join(f"site:{s}" for s in group)
            url = f"https://news.google.com/rss/search?q={keyword} ({site_q})&hl=ko&gl=KR&ceid=KR:ko"
            items = _fetch_rss(url)
            
            # 단계별 폴백: 그룹 검색 실패 시 사이트 제한 없이 해당 그룹 키워드 검색
            if not items:
                url_fb1 = f"https://news.google.com/rss/search?q={keyword} {group[0]}&hl=ko&gl=KR&ceid=KR:ko"
                items = _fetch_rss(url_fb1)
            
            random.shuffle(items)
            parsed = _parse_items(items, mode, seen, per_group)
            results.extend(parsed)

        # 전체 결과가 부족할 경우 최후의 수단: 가장 포괄적인 키워드로 검색
        if len(results) < sample_size:
            url_fb2 = f"https://news.google.com/rss/search?q=마케팅 브랜딩 트렌드&hl=ko&gl=KR&ceid=KR:ko"
            extra_items = _fetch_rss(url_fb2)
            extra_parsed = _parse_items(extra_items, mode, seen, sample_size - len(results))
            results.extend(extra_parsed)

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

