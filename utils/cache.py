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

