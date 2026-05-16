from html import unescape
from datetime import datetime
from zoneinfo import ZoneInfo
from src.utils.instagram_downloader import extract_instagram_post
from src.utils.caption_utils import format_instagram_caption
from src.handlers.telegram_handler import (
    _send_admin_message,
    _send_photo,
    _send_video,
    _send_media_group
)

async def process_instagram_post(url):

    try:
        post = await extract_instagram_post(url)
    except Exception as e:
        error_msg = (
            f"[IG POST] ❌ extract error:\n\n"
            f"{str(e)}"
        )

        print(error_msg)

        await _send_admin_message(
            error_msg
        )
        
        return False

    # =====================
    # DATA
    # =====================

    name = post["name"]
    instagram_user = (
        post["username"]
    )
    link = post["link"]
    date = post["date"]
    description = unescape(
        post.get("description")
        or ""
    )

    timestamp = None

    if date:
        dt = datetime.strptime(
            date,
            "%Y-%m-%d %H:%M:%S"
        )

        dt = dt.replace(
            tzinfo=ZoneInfo("UTC")
        )

        dt_wib = dt.astimezone(
            ZoneInfo(
                "Asia/Jakarta"
            )
        )

        timestamp = int(
            dt_wib.timestamp()
        )

    # =====================
    # CAPTION
    # =====================

    caption = format_instagram_caption(
        name,
        instagram_user,
        link,
        timestamp = timestamp,
        description = description
    )

    # =====================
    # MEDIA GROUP
    # =====================

    media_group = []

    for i, media in enumerate(
        post["media"]
    ):

        media_item = {
            "type": media["type"],
            "media": media["media"]
        }

        # =====================
        # FIRST ITEM CAPTION
        # =====================

        if i == 0:
            media_item["caption"] = (
                caption
            )
            media_item["parse_mode"] = (
                "HTML"
            )
        media_group.append(
            media_item
        )

    # =====================
    # SEND
    # =====================

    try:

        # =====================
        # SINGLE MEDIA
        # =====================

        if len(media_group) == 1:

            media = media_group[0]

            if media["type"] == "photo":

                await _send_photo(
                    media["media"],
                    caption=media.get(
                        "caption"
                    ),
                    parse_mode="HTML"
                )

            else:

                await _send_video(
                    media["media"],
                    caption=media.get(
                        "caption"
                    ),
                    parse_mode="HTML"
                )

        # =====================
        # MULTIPLE MEDIA
        # =====================

        else:

            await _send_media_group(
                media_group
            )

        return True

    except Exception as e:

        print(
            "[IG POST] ❌ send error:",
            e
        )

        return False