import json
import asyncio

COOKIE_FILE = "data/cookies/cookies.txt"

TARGETS_FILE = "data/targets.json"

def load_targets():
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_target_name(
    instagram_user
):
    targets = load_targets()

    for name, accounts in (
        targets.items()
    ):
        if (accounts.get("instagram") == instagram_user):
            return name
    return instagram_user

async def extract_instagram_post(url):
    proc = await asyncio.create_subprocess_exec(
        "python3",
        "-m",
        "gallery_dl",
        "--cookies",
        COOKIE_FILE,
        "-j",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(
            stderr.decode().strip()
        )
    
    if not stdout:
        raise Exception(
            "Empty gallery-dl output"
        )
    
    try:
        raw_data = json.loads(
            stdout.decode()
        )
    except Exception as e:
        raise Exception(
            f"JSON parse error: {e}"
        )

    if not raw_data:
        raise Exception("Empty response")

    # =====================
    # METADATA
    # =====================

    post = None
    for entry in raw_data:

        if (
            isinstance(entry, list)
            and len(entry) >= 2
            and isinstance(
                entry[-1],
                dict
            )
        ):

            post = entry[-1]
            break

    if not post:
        raise Exception(
            "Post metadata not found"
        )

    instagram_user = post.get(
        "username"
    )

    name = get_target_name(
        instagram_user
    )

    # =====================
    # MEDIA
    # =====================

    media = []

    for entry in raw_data:

        if (
            not isinstance(entry, list)
            or len(entry) < 3
            or not isinstance(
                entry[2],
                dict
            )
        ):
            continue

        media_data = entry[2]

        extension = (
            media_data.get(
                "extension"
            )
            or ""
        ).lower()

        # =====================
        # VIDEO
        # =====================

        if extension == "mp4":
            media_type = "video"
            media_url = (
                media_data.get(
                    "video_url"
                )
                or entry[1]
            )

        # =====================
        # PHOTO
        # =====================

        else:
            media_type = "photo"
            media_url = (
                media_data.get(
                    "display_url"
                )
                or entry[1]
            )
        media.append({
            "type": media_type,
            "media": media_url
        })

    # =====================
    # FINAL RESULT
    # =====================

    return {
        "name": name,
        "username": instagram_user,
        "link": post.get(
            "post_url"
        ),
        "date": post.get(
            "post_date"
        ),
        "description": post.get(
            "description"
        ),
        "media": media
    }