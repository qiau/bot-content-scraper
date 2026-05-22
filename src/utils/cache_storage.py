import json
import os

CACHE_DIR = "data/cache"

def get_cache_file(platform):
    return os.path.join(CACHE_DIR, f"{platform}_cache.json")

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


def update_cache(cache, username, new_items, max_size=3):
    user_cache = cache.setdefault(username, {})

    for item in new_items:

        user_cache[
            str(item["id"])
        ] = int(item["timestamp"])

    # =====================================
    # SORT TIMESTAMP
    # TERBARU -> TERLAMA
    # =====================================

    sorted_items = sorted(
        user_cache.items(),
        key=lambda x: x[1],
        reverse=True
    )

    sorted_items = sorted_items[:max_size]

    cache[username] = dict(sorted_items)

    return cache