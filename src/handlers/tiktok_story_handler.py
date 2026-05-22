import asyncio
import random

from src.services.tiktok_story_service import (
    get_tiktok_story
)

from src.handlers.telegram_handler import (
    send_photo,
    send_video,
    send_media_group,
    send_admin_message
)
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_tiktok_story_caption
from src.utils.tiktok_downloader import extract_tiktok_data

async def process_tiktok_story(name, accounts, cache, semaphore):
    tiktok_user = accounts.get("tiktok")
    if not tiktok_user:
        return

    async with semaphore:
        await asyncio.sleep(1)

        story_ids = []

        for attempt in range(2):
            try:
                story_ids = await get_tiktok_story(tiktok_user)
                break

            except Exception as e:
                await send_admin_message(
                    f"{tiktok_user}: gagal ambil story "
                    f"(attempt {attempt + 1}): {e}"
                )

            await asyncio.sleep(
                random.uniform(4, 6)
            )

        if not story_ids:
            print(f"{tiktok_user}: no story")
            return

        user_cache = cache.get(tiktok_user, {})
        latest_cached_id = int(
            next(iter(user_cache), 0)
        ) 
        new_story_ids = []

        for story_id in story_ids:
            if int(story_id) <= latest_cached_id:
                continue

            new_story_ids.append(story_id)

        if not new_story_ids:
            print(f"{tiktok_user}: no new story")
            return
        
        media_items = []
        new_stories = []

        for story_id in new_story_ids:
            link = f"https://www.tiktok.com/@{tiktok_user}/video/{story_id}"
            try:
                result = await extract_tiktok_data(link)
                if not result:
                    continue

                media_items.append(result) 
                new_stories.append({
                    "id": story_id,
                    "timestamp": result["create_time"]
                })

                await asyncio.sleep(
                    random.uniform(3, 4)
                )

            except Exception as e:
                await send_admin_message(
                    f"{tiktok_user}: gagal ambil media "
                    f"{story_id}: {e}"
                )

        if not media_items:
            return
        
        latest_story = new_stories[-1]
        caption = (
            format_tiktok_story_caption(
                name,
                tiktok_user,
                (
                    "https://www.tiktok.com/"
                    f"@{tiktok_user}/video/"
                    f"{latest_story['id']}"
                ),
                latest_story["timestamp"]
            )
        )

        try:
            if len(media_items) == 1:
                media = media_items[0]

                if media["type"] == "video":
                    await send_video(
                        media["data"],
                        caption=caption,
                        parse_mode="HTML"
                    )

                elif media["type"] == "image":
                    await send_photo(
                        media["data"],
                        caption=caption,
                        parse_mode="HTML"
                    )

            else:
                media_group = []

                for media in media_items:

                    if media["type"] == "video":
                        media_group.append({
                            "type": "video",
                            "media": media["data"]
                        })

                    elif media["type"] == "image":
                        media_group.append({
                            "type": "photo",
                            "media": media["data"]
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

            update_cache(
                cache,
                tiktok_user,
                new_stories
            )

        except Exception as e:
            await send_admin_message(
                f"{tiktok_user}: gagal kirim story: {e}"
            )