import json
import os

CACHE_FILE = "data/cache.json"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Cache rusak, reset:", e)
        return {}


def save_cache(data):
    temp_file = CACHE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(temp_file, CACHE_FILE)


def update_cache(cache, username, platform, new_ids, max_size=3):
    user_cache = cache.setdefault(username, {})
    platform_cache = user_cache.setdefault(platform, [])

    combined = new_ids + platform_cache

    seen = set()
    unique = []

    for x in combined:
        if x not in seen:
            unique.append(x)
            seen.add(x)

    user_cache[platform] = unique[:max_size]

    return cache