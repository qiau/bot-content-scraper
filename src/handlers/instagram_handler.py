from src.services.instagram_service import get_latest_posts
from src.handlers.telegram_handler import (
    send_photo, send_video, send_media_group, send_message
)
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_instagram_caption

async def process_instagram(name, accounts, cache):
    instagram_user = accounts.get("instagram")

    if not instagram_user:
        return

    posts = await get_latest_posts(instagram_user)

    if not posts:
        print(f"[IG] {instagram_user} ⚠️ no post")
        return

    user_cache = cache.get(instagram_user, {})
    new_items = []

    for post in reversed(posts):
        post_id = post.get("shortcode")

        if not post_id:
            continue

        if post_id in user_cache:
            continue

        media = post.get(
            "media"
        )

        if not media:
            continue

        link = f"https://www.instagram.com/p/{post_id}/"
        
        caption = format_instagram_caption(
            name, instagram_user,
            link,
            post.get("post_date"),
            post.get("description")
        )

        media_group = []

        for i, item in enumerate(media):
            media_item = {
                "type": (
                    "video"
                    if item["type"] == "video"
                    else "photo"
                ),
                "media": item["url"]
            }

            if i == 0:
                media_item["caption"] = caption
                media_item["parse_mode"] = "HTML"

            media_group.append(media_item)

        try:
            if len(media_group) == 1:
                m = media_group[0]

                if m["type"] == "photo":
                    await send_photo(m["media"], caption=m.get("caption"), parse_mode="HTML")
                else:
                    await send_video(m["media"], caption=m.get("caption"), parse_mode="HTML")

            else:
                await send_media_group(media_group)

            new_items.append({
                "id": post_id,
                "timestamp": (
                    post.get(
                        "timestamp"
                    )
                    or 0
                )
            })

        except Exception as e:
            print(f"[IG] {instagram_user} ❌ gagal kirim {post_id}:", e)
            fallback_caption = (
                f"{caption}\n\n"
                "⚠️ Media gagal dimuat, lihat langsung di Instagram"
            )

            await send_message(fallback_caption, parse_mode="HTML")
         
            new_items.append({
                "id": post_id,
                "timestamp": (
                    post.get(
                        "timestamp"
                    )
                    or 0
                )
            })

    if new_items:
        update_cache(cache, instagram_user, new_items)