import asyncio
import random

from src.services.tiktok_service import (
    get_latest_tiktoks,
    get_tiktok_video_url
)
from src.handlers.telegram_handler import (
    send_message, send_video, send_media_group
)
from src.utils.storage import update_cache

async def process_tiktok(name, accounts, cache, semaphore):
    tiktok_user = accounts.get("tiktok")

    if not tiktok_user:
        return

    async with semaphore:
        await asyncio.sleep(random.uniform(1, 2))

        try:
            videos = await get_latest_tiktoks(tiktok_user, limit=3)
        except Exception as e:
            print(f"{tiktok_user}: error {e}")
            return

        if not videos:
            print(f"{tiktok_user}: no data")
            return

        user_cache = cache.get(tiktok_user,[])
        new_ids = []

        for vid in videos:
            if vid in user_cache:
                continue

            link = f"https://www.tiktok.com/@{tiktok_user}/video/{vid}"

            try:
                result = await get_tiktok_video_url(link)
            except Exception as e:
                print(f"{tiktok_user}: downloader error {e}")
                result = None

            caption = f"🎵 {name} ({tiktok_user})\n{link}"

            try:
                if result and result.get("type") == "video":
                    await send_video(result["data"], caption=caption)

                elif result and result.get("type") == "image":
                    images = result["data"]

                    media_group = []

                    for i, img in enumerate(images):
                        item = {
                            "type": "photo",
                            "media": img.strip()
                        }

                        if i == 0:
                            item["caption"] = caption

                        media_group.append(item)

                    await send_media_group(media_group)

                else:
                    await send_message(caption)

                new_ids.append(vid)
                await asyncio.sleep(random.uniform(3, 5))

            except Exception as e:
                print(f"{tiktok_user}: gagal kirim {vid}:", e)

        if new_ids:
            update_cache(cache, tiktok_user, new_ids)
