import json
import asyncio
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    close_telegram,
)
from src.handlers.tiktok_handler import process_tiktok
from src.utils.storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime import is_running

load_dotenv()

semaphore = asyncio.Semaphore(3)

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)

async def main():

    if not is_running("tt"):
        print("⛔ TikTok mode STOP")
        return
     
    await init_telegram(os.getenv("TELEGRAM_TOKEN_SOCIAL"))

    asyncio.create_task(telegram_worker())

    cache = load_cache("tiktok")

    TARGETS = load_targets()

    tasks = []

    for name, accounts in TARGETS.items():

        if not is_running("tt"):
            print("⛔ TikTok dihentikan")
            break

        tasks.append(
            process_tiktok(
                name,
                accounts,
                cache,
                semaphore
            )
        )

    await asyncio.gather(*tasks)

    save_cache(cache, "tiktok")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())