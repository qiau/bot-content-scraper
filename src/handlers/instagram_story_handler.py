from src.handlers.telegram_handler import (
    send_photo,
    send_video,
    send_media_group,
)
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

    if stories == "ig_error":
        print(
            f"[IG STORY] "
            f"{instagram_user} ❌ IG error"
        )
        return "ig_error"

    if not stories:

        print(
            f"[IG STORY] "
            f"{instagram_user} ⚠️ no story"
        )

        return True

    user_cache = cache.get(
        instagram_user,
        {}
    )
    latest_cached_timestamp = next(
        iter(user_cache.values()), 0
    )
    new_items = []
    new_stories = []

    for story in stories:
        story_timestamp = int(
            story.get(
                "timestamp",
                0
            )
        )
        if story_timestamp <= latest_cached_timestamp:
            continue
        
        story_id = str(
            story.get(
                "story_id"
            )
        )
        new_items.append(story)
        new_stories.append({
            "id": story_id,
            "timestamp": story_timestamp
        })

    if not new_items:
        print(
            f"[IG STORY] "
            f"{instagram_user} "
            f"⚠️ no new story"
        )

        return True

    for story in new_items:
        story_id = str(
            story.get(
                "story_id"
            )
        )

        media_items = story.get(
            "media",
            []
        )
        timestamp = int(
            story.get(
                "timestamp",
                0
            )
        )
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

        try:

            if len(media_items) == 1:

                media = media_items[0]

                if media["type"] == "video":
                    await send_video(
                        media["url"],
                        caption=caption,
                        parse_mode="HTML"
                    )

                elif media["type"] == "image":
                    await send_photo(
                        media["url"],
                        caption=caption,
                        parse_mode="HTML"
                    )

            else:
                media_group = []

                for media in media_items:

                    if media["type"] == "video":
                        media_group.append({
                            "type": "video",
                            "media": media["url"]
                        })

                    elif media["type"] == "image":

                        media_group.append({
                            "type": "photo",
                            "media": media["url"]
                        })

                media_group[0]["caption"] = (
                    caption
                )

                media_group[0]["parse_mode"] = (
                    "HTML"
                )

                await send_media_group(
                    media_group
                )

        except Exception as e:
            print(
                f"[IG STORY] "
                f"{instagram_user} "
                f"❌ send error: {e}"
            )
    
    update_cache(
        cache,
        instagram_user,
        new_stories,
    )

    print(
        f"[IG STORY] "
        f"{instagram_user} "
        f"✔️ new story"
    )

    return True