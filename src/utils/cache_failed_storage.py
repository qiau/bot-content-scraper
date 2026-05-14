import json
import os

FAILED_DIR = "data/failed"

def get_failed_file(platform):
    return os.path.join(FAILED_DIR, f"{platform}.json")

def load_failed(platform):
    file = get_failed_file(platform)

    if not os.path.exists(file):
        return {}

    try:
        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except:
        return {}

def save_failed(data, platform):
    file = get_failed_file(platform)
    temp = file + ".tmp"
    
    with open(
        temp,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(temp, file)


def update_failed_post(failed, username, post):
    user_failed = failed.get(username, [])

    combined = [post] + user_failed

    seen = set()
    unique = []

    for item in combined:

        post_id = item["id"]

        if post_id in seen:
            continue

        seen.add(post_id)
        unique.append(item)

    failed[username] = unique