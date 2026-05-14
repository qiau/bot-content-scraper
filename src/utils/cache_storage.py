import json
import os

CACHE_DIR = "data/cache"

def get_cache_file(platform):
    return os.path.join(CACHE_DIR, f"{platform}.json")

def load_cache(platform):
    file = get_cache_file(platform)

    if not os.path.exists(file):
        return {}

    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Cache {platform} rusak, reset:", e)
        return {}


def save_cache(data, platform):
    file = get_cache_file(platform)
    temp = file + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(temp, file)


def update_cache(cache, username, new_posts, max_size=3):
    user_cache = cache.get(username, [])

    combined = new_posts + user_cache

    seen = set()
    unique = []

    for post in combined:
        post_id = post["id"]
        if post_id in seen:
            continue
        seen.add(post_id)
        unique.append(post)

    unique.sort(
        key=lambda x: int(x["timestamp"]),
        reverse=True
    )

    cache[username] = unique[:max_size]