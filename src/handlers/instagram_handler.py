import asyncio
import random

from src.services.instagram_service import get_latest_posts
from src.handlers.telegram_handler import (
    send_photo, send_video, send_media_group, send_message
)
from src.utils.storage import update_cache

async def process_instagram(name, accounts, cache, ig_account, proxy=None):
    instagram_user = accounts.get("instagram")
    if not instagram_user:
        return None

    posts = await get_latest_posts(instagram_user, ig_account, proxy=proxy)

    if posts is None:
        print(f"[IG] {instagram_user} ❌ fetch error (proxy kemungkinan bermasalah)")
        return None

    if not posts:
        print(f"[IG] {instagram_user} ⚠️ no post")
        return True

    user_cache = cache.get(instagram_user, [])
    new_ids = []

    for post in posts:
        post_id = post["shortcode"]

        if post_id in user_cache:
            continue

        link = f"https://www.instagram.com/p/{post_id}/"
        caption = f"📸 {name} ({instagram_user})\n{link}"

        media_group = []

        for i, m in enumerate(post["media"]):
            media_item = {
                "type": "video" if m["type"] == "video" else "photo",
                "media": m["url"]
            }

            if i == 0:
                media_item["caption"] = caption

            media_group.append(media_item)

        try:
            if len(media_group) == 1:
                m = media_group[0]

                if m["type"] == "photo":
                    await send_photo(m["media"], caption=m.get("caption"))
                else:
                    await send_video(m["media"], caption=m.get("caption"))

            else:
                await send_media_group(media_group)

            new_ids.append(post_id)
            await asyncio.sleep(random.uniform(3, 5))

        except Exception as e:
            print(f"[IG] {instagram_user} ❌ gagal kirim {post_id}:", e)
            fallback_caption = (
                f"{caption}\n\n"
                "⚠️ Media gagal dimuat, lihat langsung di Instagram"
            )

            await send_message(fallback_caption)
            new_ids.append(post_id)
            await asyncio.sleep(random.uniform(3, 5))

    if new_ids:
        update_cache(cache, instagram_user, new_ids)
    
    return True