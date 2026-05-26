from src.services.instagram_service import get_instagram_posts
from src.handlers.telegram_handler import send_photo, send_video, send_media_group, send_message
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_instagram_caption

async def process_instagram_post(name, accounts, cache, session):
    instagram_user = accounts.get("instagram")
    instagram_user_id = accounts.get("instagram_user_id")

    if not instagram_user:
        return "skip"

    posts = await get_instagram_posts(instagram_user, instagram_user_id, session)

    # =========================
    # SERVICE ERROR
    # =========================

    if posts == "rate_limit":
        return "rate_limit"

    if posts == "auth_error":
        return "auth_error"

    if posts == "ig_error":

        print(
            f"[IG] {instagram_user} "
            f"❌ IG error"
        )

        return "ig_error"

    # =========================
    # EMPTY
    # =========================
    if not posts:
        print(f"[IG] {instagram_user} ⚠️ no post")
        return True

    user_cache = cache.get(instagram_user, {})
    latest_cached_timestamp = next(
        iter(user_cache.values()), 0
    )

    new_items = []

    for post in reversed(posts):
        timestamp = post.get("timestamp")
        if timestamp <= latest_cached_timestamp:
            continue

        post_id = post.get("id")

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
            timestamp,
            post.get("description") 
        )

        media_group = []

        for i, item in enumerate(media):
            media_item = {
                "type": "video" if item["type"] == "video" else "photo",
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
                "timestamp": timestamp
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
                "timestamp": timestamp
            })

    if new_items:
        update_cache(cache, instagram_user, new_items)

    return True