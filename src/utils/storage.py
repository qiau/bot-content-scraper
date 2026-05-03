import json
import os

CACHE_DIR = "data"

def get_cache_file(platform):
    return os.path.join(CACHE_DIR, f"cache_{platform}.json")

def load_cache(platform):
    cache_file = get_cache_file(platform)

    if not os.path.exists(cache_file):
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Cache {platform} rusak, reset:", e)
        return {}


def save_cache(data, platform):
    cache_file = get_cache_file(platform)
    temp_file = cache_file + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(temp_file, cache_file)


def update_cache(cache, username, new_ids, max_size=3):
    user_cache = cache.setdefault(username, [])

    combined = new_ids + user_cache

    seen = set()
    unique = []

    for x in combined:
        if x not in seen:
            unique.append(x)
            seen.add(x)

    cache[username] = unique[:max_size]

    return cache