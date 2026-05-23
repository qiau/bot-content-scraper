import json
import asyncio
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    close_telegram,
)
from src.handlers.tiktok_handler import process_tiktok
from src.handlers.tiktok_story_handler import process_tiktok_story
from src.utils.cache_storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime_state import is_running

load_dotenv()

semaphore = asyncio.Semaphore(3)

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)

async def main():

    if not is_running("tiktok"):
        print("⛔ TikTok mode STOP")
        return
     
    await init_telegram(os.getenv("TELEGRAM_TOKEN_SOCIAL"))

    asyncio.create_task(telegram_worker())

    post_cache = load_cache("tiktok_posts")
    story_cache = load_cache("tiktok_stories")

    targets = load_targets()

    tasks = []

    for name, accounts in targets.items():

        if not is_running("tiktok"):
            print("⛔ TikTok dihentikan")
            break

        tasks.append(
            process_tiktok(
                name=name,
                accounts=accounts,
                cache=post_cache,
                semaphore=semaphore
            )
        )

        tasks.append(
            process_tiktok_story(
                name=name,
                accounts=accounts,
                cache=story_cache,
                semaphore=semaphore
            )
        )

    await asyncio.gather(*tasks)

    save_cache(post_cache, "tiktok_posts")
    save_cache(story_cache, "tiktok_stories")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())