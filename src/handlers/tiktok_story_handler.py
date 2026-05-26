import asyncio
import random

from src.services.tiktok_story_service import get_tiktok_story
from src.handlers.telegram_handler import send_photo,send_video,send_admin_message
from src.utils.cache_storage import update_cache
from src.utils.caption_utils import format_tiktok_story_caption
from src.utils.tiktok_downloader import extract_tiktok_data

async def process_tiktok_story(
    name,
    accounts,
    cache,
    semaphore
):
    tiktok_user = accounts.get(
        "tiktok"
    )

    if not tiktok_user:
        return "skip"

    async with semaphore:

        await asyncio.sleep(1)

        # =========================
        # GET STORY IDS
        # =========================

        story_ids = []

        for attempt in range(2):

            try:
                story_ids = await (
                    get_tiktok_story(
                        tiktok_user
                    )
                )

                break

            except Exception as e:
                await send_admin_message(
                    f"{tiktok_user}: "
                    f"gagal ambil story "
                    f"(attempt {attempt + 1}): {e}"
                )

            await asyncio.sleep(
                random.uniform(4, 6)
            )

        # =========================
        # EMPTY
        # =========================

        if not story_ids:
            print(
                f"{tiktok_user}: no story"
            )
            return True

        # =========================
        # CACHE
        # =========================

        user_cache = cache.get(
            tiktok_user,
            {}
        )

        latest_cached_id = int(
            next(
                iter(user_cache),
                0
            )
        )

        # =========================
        # PROCESS STORIES
        # =========================

        new_stories = []

        for story_id in story_ids:

            if int(story_id) <= latest_cached_id:
                continue

            link = (
                "https://www.tiktok.com/"
                f"@{tiktok_user}/video/"
                f"{story_id}"
            )

            try:
                result = await (
                    extract_tiktok_data(
                        link
                    )
                )
                if not result:
                    continue

                timestamp = result.get("create_time")
                caption = (
                    format_tiktok_story_caption(
                        name,
                        tiktok_user,
                        link,
                        timestamp
                    )
                )

                # =========================
                # SEND TELEGRAM
                # =========================

                if result["type"] == "video":
                    await send_video(
                        result["data"],
                        caption=caption,
                        parse_mode="HTML"
                    )

                else:
                    await send_photo(
                        result["data"],
                        caption=caption,
                        parse_mode="HTML"
                    )

                print(
                    f"[TT STORY] "
                    f"{tiktok_user} "
                    f"✔️ new story "
                    f"{story_id}"
                )

                new_stories.append({
                    "id": story_id,
                    "timestamp": timestamp
                })

                await asyncio.sleep(
                    random.uniform(3, 4)
                )

            except Exception as e:
                await send_admin_message(
                    f"{tiktok_user}: "
                    f"gagal process story "
                    f"{story_id}: {e}"
                )

                continue

        # =========================
        # UPDATE CACHE
        # =========================

        if new_stories:
            update_cache(
                cache,
                tiktok_user,
                new_stories
            )

        return True