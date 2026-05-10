import asyncio
import random

from src.services.x_service import get_latest_tweets
from src.handlers.telegram_handler import (
    send_message, send_photo, send_video, send_media_group
)
from src.utils.storage import update_cache
from src.utils.x_video_downloader import extract_media_urls
from src.utils.caption import format_x_caption

async def process_x(name, accounts, cache, semaphore):
    x_user = accounts.get("x")
    if not x_user:
        return

    async with semaphore:
        await asyncio.sleep(random.uniform(2, 3))

        posts = []

        for attempt in range(2):

            try:

                posts = await get_latest_tweets(
                    x_user,
                    limit=3
                )

                if posts:
                    break

            except Exception as e:

                print(
                    f"{x_user}: "
                    f"retry {attempt + 1} "
                    f"error {e}"
                )

            await asyncio.sleep(
                random.uniform(2, 4)
            )

        if not posts:
            print(f"{x_user}: no data")
            return

        user_cache = cache.get(x_user,[])
        latest_cached_id = max(
            map(int, user_cache),
            default=0
        )
        new_ids = []

        for post in reversed(posts):
            tweet_id = post["id"]

            if int(tweet_id) <= latest_cached_id:
                continue

            tweet_url = post["url"]
            images = post["images"]
            has_video = post["has_video"]

            caption = format_x_caption(
                name, x_user,
                tweet_url,
                post.get("timestamp"),
                post.get("text")
            )

            media_group = []

            for img in images:
                item = {
                    "type": "photo",
                    "media": img
                }

                if not media_group:
                    item["caption"] = caption
                    item["parse_mode"] = "HTML"

                media_group.append(item)

            if has_video:
                videos, video_error, failed_count = extract_media_urls(tweet_url)

                if video_error and not videos:
                    msg = (
                        f"{caption}\n\n"
                        f"⚠️ {failed_count} "
                        f"video gagal didownload"
                    )

                    await send_message(
                        msg,
                        parse_mode="HTML"
                    )

                    new_ids.append(tweet_id)
                    continue

                for v in videos:
                    item = {
                        "type": "video",
                        "media": v
                    }

                    if not media_group:
                        extra = ""
                        
                        if video_error:
                            extra = (
                                f"\n\n⚠️ "
                                f"{failed_count} "
                                f"video gagal didownload"
                            )

                        item["caption"] = caption + extra
                        item["parse_mode"] = "HTML"

                    media_group.append(item)

            if not media_group:
                continue

            try:
                if len(media_group) == 1:
                    m = media_group[0]
                    media = m["media"]

                    if m["type"] == "photo":
                        await send_photo(media, caption=m.get("caption"), parse_mode="HTML")
                    else:
                        await send_video(media, caption=m.get("caption"), parse_mode="HTML")

                else:
                    await send_media_group(media_group)

                new_ids.append(tweet_id)

            except Exception as e:
                print(f"{x_user}: gagal kirim {tweet_id}:", e)

            await asyncio.sleep(random.uniform(2, 3))

        if new_ids:
            update_cache(cache, x_user, new_ids)
