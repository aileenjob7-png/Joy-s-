import os
import json
from datetime import datetime

CACHE_DIR = "cache"

def get_weekly_cache_filename(mode: str) -> str:
    """Returns a filename based on the current year and ISO week number."""
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return os.path.join(CACHE_DIR, f"{mode}_{year}_W{week:02d}.json")

def load_weekly_cache(mode: str):
    """Loads the cached data for the current week if it exists."""
    filename = get_weekly_cache_filename(mode)
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_weekly_cache(mode: str, data: list):
    """Saves the fetched data to a cache file for the current week."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    filename = get_weekly_cache_filename(mode)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def get_all_historical_titles(mode: str) -> set:
    """역대 모든 캐시 파일을 읽어 기사 제목 세트를 반환합니다."""
    titles = set()
    if not os.path.exists(CACHE_DIR):
        return titles
    
    for f in os.listdir(CACHE_DIR):
        if f.startswith(mode) and f.endswith(".json"):
            try:
                with open(os.path.join(CACHE_DIR, f), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for item in data:
                        titles.add(item.get('title'))
            except Exception:
                continue
    return titles

def get_history_file_list(mode: str) -> list:
    """과거 캐시 파일 목록을 내림차순(최신순)으로 반환합니다."""
    history = []
    if not os.path.exists(CACHE_DIR):
        return history
    
    # 예: study_2026_W10.json -> (2026, 10, 파일명)
    for f in os.listdir(CACHE_DIR):
        if f.startswith(mode) and f.endswith(".json"):
            parts = f.replace(".json", "").split("_")
            if len(parts) >= 3:
                history.append({
                    "year": parts[1],
                    "week": parts[2].replace("W", ""),
                    "filename": f
                })
    
    # 최신 주차부터 정렬
    history.sort(key=lambda x: (x['year'], x['week']), reverse=True)
    return history

def load_cache_by_filename(filename: str):
    """특정 파일명으로 캐시 데이터를 로드합니다."""
    path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

