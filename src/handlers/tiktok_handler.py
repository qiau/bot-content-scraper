import asyncio
import random

from src.services.tiktok_service import (
    get_latest_tiktoks,
    get_tiktok_video_url
)
from src.handlers.telegram_handler import (
    send_message, send_video, send_media_group
)
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_tiktok_caption

async def process_tiktok(name, target, cache, failed, semaphore):
    tiktok_user = target.get("tiktok")
    if not tiktok_user:
        return

    async with semaphore:
        await asyncio.sleep(random.uniform(2, 3))

        videos = []

        for attempt in range(3):
            try:
                videos = await get_latest_tiktoks(
                    tiktok_user,
                    limit=3
                )

                if videos:
                    break

            except Exception as e:
                print(
                    f"{tiktok_user}: retry "
                    f"{attempt + 1} error {e}"
                )

            await asyncio.sleep(
                random.uniform(5, 8)
            )

        if not videos:
            print(f"{tiktok_user}: no data")
            return

        user_cache = cache.get(tiktok_user,[])

        latest_cached_timestamp = 0

        if user_cache:
            latest_cached_timestamp = (
                user_cache[0]["timestamp"]
            )
        new_posts = []

        for vid in reversed(videos):

            link = f"https://www.tiktok.com/@{tiktok_user}/video/{vid}"

            try:
                result = await get_tiktok_video_url(link)
            except Exception as e:
                print(f"{tiktok_user}: downloader error {e}")
                result = None

            if not result:
                continue

            timestamp = result.get("create_time", 0)
            
            if (timestamp <= latest_cached_timestamp):
                continue

            description = result.get("description", None) 

            type = result.get("type")

            caption = format_tiktok_caption(
                name, tiktok_user,
                link,
                timestamp,
                description
            )

            failed_meta = (
                failed,
                tiktok_user,
                {
                    "id": vid,
                    "timestamp": timestamp,
                    "url": link,
                    "retries": 0
                }
            )

            if type == "video":
                await send_video(
                    result["data"],
                    caption=caption,
                    parse_mode="HTML",
                    failed_meta=failed_meta
                )

            elif type == "image":
                images = result["data"]

                media_group = []

                for i, img in enumerate(images):
                    item = {
                        "type": "photo",
                        "media": img.strip()
                    }

                    if i == 0:
                        item["caption"] = caption
                        item["parse_mode"] = "HTML"

                    media_group.append(item)

                await send_media_group(
                    media_group,
                    failed_meta=failed_meta
                )

            else:
                await send_message(
                    caption, 
                    parse_mode="HTML", 
                    failed_meta=failed_meta
                )

            new_posts.append({
                "id": vid,
                "timestamp": timestamp
            })

        await asyncio.sleep(random.uniform(2, 3))

        if new_posts: 
            update_cache(cache, tiktok_user, new_posts)
