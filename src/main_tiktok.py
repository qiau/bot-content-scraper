import json
import asyncio
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    close_telegram,
)
from src.handlers.tiktok_handler import process_tiktok
from src.services.running_error_service import error_service
from src.utils.cache_storage import load_cache, save_cache
from src.utils.cache_failed_storage import load_failed, save_failed
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime_state import is_running

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
    failed = load_failed("tiktok")

    if failed:
        error_service(cache, failed)

    TARGETS = load_targets()

    tasks = []

    for name, target in TARGETS.items():

        if not is_running("tt"):
            print("⛔ TikTok dihentikan")
            break

        tasks.append(
            process_tiktok(
                name,
                target,
                cache, 
                failed,
                semaphore
            )
        )

    try:
        await asyncio.gather(*tasks)
        await telegram_queue.join()

    finally:
        save_cache(cache, "tiktok")
        save_failed(failed, "tiktok")
        await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())