import asyncio
import random

from src.services.tiktok_service import get_tiktok_post

from src.handlers.telegram_handler import (
    send_message, send_video, send_media_group, send_admin_message
)
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_tiktok_caption
from src.utils.tiktok_downloader import extract_tiktok_data

async def process_tiktok(name, accounts, cache, semaphore):
    tiktok_user = accounts.get("tiktok")
    if not tiktok_user:
        return

    async with semaphore:
        await asyncio.sleep(random.uniform(2, 3))

        videos = []

        for attempt in range(3):
            try:
                videos = await get_tiktok_post(
                    tiktok_user,
                    limit=3
                )
                if videos:
                    break

            except Exception as e:
                await send_admin_message(
                    f"Error ambil TikTok {tiktok_user} (attempt {attempt + 1}): {e}"
                )

            await asyncio.sleep(
                random.uniform(5, 8)
            )

        if not videos:
            print(f"{tiktok_user}: no data")
            return

        user_cache = cache.get(tiktok_user, {})
        latest_cached_id = int(
            next(iter(user_cache), 0)
        )
        new_items = []

        for vid in reversed(videos):
            # skip video lama
            if int(vid) <= latest_cached_id:
                continue

            link = f"https://www.tiktok.com/@{tiktok_user}/video/{vid}"

            try:
                result = await extract_tiktok_data(link)
                if not result:
                    continue
                
            except Exception as e:
                await send_admin_message(f"{tiktok_user}: gagal download {link}: {e}")
                continue
           
            type = result["type"]
            timestamp = result["create_time"]
            description = result["description"]

            caption = format_tiktok_caption(
                name, tiktok_user,
                link,
                timestamp,
                description
            )

            try:
                if result and type == "video":
                    await send_video(result["data"], caption=caption, parse_mode="HTML")

                elif result and type == "image":
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

                    await send_media_group(media_group)

                else:
                    await send_message(caption, parse_mode="HTML")

                new_items.append({
                    "id": vid,
                    "timestamp": timestamp
                })

            except Exception as e:
                await send_admin_message(f"{tiktok_user}: gagal kirim {link}: {e}")

            await asyncio.sleep(random.uniform(2, 3))

        if new_items:
            update_cache(cache, tiktok_user, new_items)
