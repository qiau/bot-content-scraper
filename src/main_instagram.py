import json
import asyncio
import aiohttp
import random
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    _send_admin_message,
    init_telegram,
    close_telegram
)
from src.handlers.instagram_handler import process_instagram_post
from src.handlers.instagram_story_handler import process_instagram_story
from src.services.instagram_service import load_cookies, build_headers

from src.utils.cache_storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime_state import set_mode, is_running, get_next_instagram_batch, get_next_instagram_account

load_dotenv()
SPLIT_DIR = "data/target_splits"

def load_targets(batch_id):
    file_path = (
        f"{SPLIT_DIR}/"
        f"targets_{batch_id}.json"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
def get_total_batches():
    files = [

        f for f in os.listdir(
            SPLIT_DIR
        )

        if (
            f.startswith(
                "targets_"
            )
            and f.endswith(
                ".json"
            )
        )
    ]

    return len(files)

async def main():

    if not is_running("instagram"):
        print("⛔ IG mode STOP (skip run)")
        return
    
    delay = random.randint(0, 3) 
    await asyncio.sleep(delay)
    
    await init_telegram(os.getenv("TELEGRAM_TOKEN_IG"))
    
    asyncio.create_task(telegram_worker())

    post_cache = load_cache("instagram_posts")
    story_cache = load_cache("instagram_stories")

    total_batches = (
        get_total_batches()
    )

    batch_id = (
        get_next_instagram_batch(
            total_batches
        )
    )

    targets = load_targets(batch_id)

    account_id = (
        get_next_instagram_account()
    )

    cookie_file = (
        f"data/cookies/"
        f"cookies_{account_id}.txt"
    )

    cookies = load_cookies(
        cookie_file
    )
    headers = build_headers()

    timeout = aiohttp.ClientTimeout(
        total=30,
        connect=10,
        sock_read=20
    )

    should_stop_after_run = False

    fail_count = 0

    async with aiohttp.ClientSession(
        headers=headers,
        cookies=cookies,
        timeout=timeout
    ) as session:
        for name, accounts in (
            targets.items()
        ):

            if not is_running(
                "instagram"
            ):
                print(
                    "⛔ Dihentikan"
                )
                await _send_admin_message("⛔ IG scraper dihentikan manual")
                break

            post_result = await process_instagram_post(
                name,
                accounts,
                post_cache,
                session
            )
            
            await asyncio.sleep(random.uniform(2,5))

            story_result = await process_instagram_story(
                name,
                accounts,
                story_cache,
                session
            )

            if (
                post_result == "rate_limit"
                or story_result == "rate_limit"
            ):
                fail_count += 1
                await _send_admin_message(
                    f"⚠️ Rate limit Instagram\n"
                    f"Target: {name}\n"
                    f"Fail count: {fail_count}"
                )
                print("😴 Rate limit cooldown 1 menit...")
                await asyncio.sleep(60)

            elif (
                post_result == "ig_error"
                or story_result == "ig_error"
            ):
                print(
                    f"⚠️ IG error "
                    f"{name}"
                )

            elif post_result == "skip":
                await _send_admin_message(
                    f"Target: {name}\n"
                    f"di skip karena tidak ada username IG"
                )
                pass

            else:
                fail_count = 0

            if fail_count >= 2:
                await _send_admin_message(
                    f"🚨 IG account "
                    f"{account_id} error"
                )

                should_stop_after_run = True

                break

            sleep_time = random.uniform(35,90)
            await asyncio.sleep(sleep_time)

    save_cache(post_cache, "instagram_posts")
    save_cache(story_cache, "instagram_stories")

    if should_stop_after_run:
        await _send_admin_message("⛔ IG dihentikan (berlaku untuk run berikutnya)")
        set_mode("instagram", "stopped")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())