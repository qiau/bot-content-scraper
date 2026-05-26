from src.handlers.telegram_handler import send_photo,send_video
from src.services.instagram_story_service import get_instagram_story
from src.utils.caption_utils import format_instagram_story_caption
from src.utils.cache_storage import update_cache

async def process_instagram_story(
    name,
    accounts,
    cache,
    session
):

    instagram_user = accounts.get(
        "instagram"
    )

    instagram_user_id = accounts.get(
        "instagram_user_id"
    )

    if not instagram_user:
        return "skip"

    stories = await get_instagram_story(
        instagram_user,
        instagram_user_id,
        session
    )

    # =========================
    # SERVICE ERROR
    # =========================

    if stories == "rate_limit":
        return "rate_limit"

    if stories == "auth_error":
        return "auth_error"

    if stories == "ig_error":

        print(
            f"[IG STORY] "
            f"{instagram_user} ❌ IG error"
        )

        return "ig_error"

    # =========================
    # EMPTY
    # =========================

    if not stories:

        print(
            f"[IG STORY] "
            f"{instagram_user} ⚠️ no story"
        )

        return True

    # =========================
    # CACHE
    # =========================

    user_cache = cache.get(
        instagram_user,
        {}
    )

    latest_cached_timestamp = next(
        iter(user_cache.values()),
        0
    )

    new_stories = []

    # =========================
    # PROCESS STORIES
    # =========================

    for story in stories:
        story_id = str(
            story.get(
                "story_id"
            )
        )

        if not story_id:
            continue

        timestamp = int(
            story.get(
                "timestamp",
                0
            )
        )

        if timestamp <= latest_cached_timestamp:
            continue

        if story_id in user_cache:
            continue

        media_items = story.get(
            "media",
            []
        )

        if not media_items:
            continue

        media = media_items[0]

        caption = (
            format_instagram_story_caption(
                name,
                instagram_user,
                (
                    "https://www.instagram.com/stories/"
                    f"{instagram_user}/{story_id}/"
                ),
                timestamp
            )
        )

        # =========================
        # SEND TELEGRAM
        # =========================

        try:
            if media["type"] == "image":
                await send_photo(
                    media["url"],
                    caption=caption,
                    parse_mode="HTML"
                )

            else:
                await send_video(
                    media["url"],
                    caption=caption,
                    parse_mode="HTML"
                )

            print(
                f"[IG STORY] "
                f"{instagram_user} "
                f"✔️ new story {story_id}"
            )

        except Exception as e:
            print(
                f"[IG STORY] "
                f"{instagram_user} "
                f"❌ send error "
                f"{story_id}: {e}"
            )

            continue

        # =========================
        # SAVE CACHE ITEM
        # =========================

        new_stories.append({
            "id": story_id,
            "timestamp": timestamp
        })

    # =========================
    # UPDATE CACHE
    # =========================

    if new_stories:
        update_cache(
            cache,
            instagram_user,
            new_stories,
        )

    return True