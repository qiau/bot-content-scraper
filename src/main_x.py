import json
import asyncio
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    close_telegram,
)
from src.handlers.x_handler import process_x
from src.utils.storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue

load_dotenv()

with open("data/targets.json", "r") as f:
    TARGETS = json.load(f)

semaphore = asyncio.Semaphore(3)

async def main():
    await init_telegram(os.getenv("TELEGRAM_TOKEN_SOCIAL"))
    asyncio.create_task(telegram_worker())

    cache = load_cache("x")

    tasks = [
        process_x(name, accounts, cache, semaphore)
        for name, accounts in TARGETS.items()
    ]

    await asyncio.gather(*tasks)

    save_cache(cache, "x")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())