import asyncio
import random

from src.services.x_service import get_latest_tweets
from src.handlers.telegram_handler import (
    send_message, send_photo, send_video, send_media_group
)
from src.utils.storage import update_cache
from src.utils.x_video_downloader import extract_media_urls

async def process_x(name, accounts, cache, semaphore):
    x_user = accounts.get("x")
    if not x_user:
        return

    async with semaphore:
        await asyncio.sleep(random.uniform(2, 3))

        try:
            posts = await get_latest_tweets(x_user, limit=3)
        except Exception as e:
            print(f"{x_user}: error {e}")
            return

        if not posts:
            print(f"{x_user}: no data")
            return

        user_cache = cache.get(x_user,[])
        new_ids = []

        for post in posts:
            tweet_id = post["id"]

            if tweet_id in user_cache:
                continue

            tweet_url = post["url"]
            images = post["images"]
            has_video = post["has_video"]

            caption = f"🐦 {name} ({x_user})\n{tweet_url}"

            media_group = []

            for img in images:
                item = {
                    "type": "photo",
                    "media": img
                }

                if not media_group:
                    item["caption"] = caption

                media_group.append(item)

            if has_video:
                videos, video_error, failed_count = extract_media_urls(tweet_url)

                if video_error and not videos:
                    msg = f"{caption}\n\n⚠️ {failed_count} video gagal didownload"
                    await send_message(msg)

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
                            extra = f"\n\n⚠️ {failed_count} video gagal didownload"

                        item["caption"] = caption + extra

                    media_group.append(item)

            if not media_group:
                continue

            try:
                if len(media_group) == 1:
                    m = media_group[0]

                    if m["type"] == "photo":
                        await send_photo(m["media"], caption=m.get("caption"))
                    else:
                        await send_video(m["media"], caption=m.get("caption"))

                else:
                    await send_media_group(media_group)

                new_ids.append(tweet_id)

            except Exception as e:
                print(f"{x_user}: gagal kirim {tweet_id}:", e)

        if new_ids:
            update_cache(cache, x_user, new_ids)
