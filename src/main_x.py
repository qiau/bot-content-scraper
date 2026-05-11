import json
import asyncio
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    close_telegram,
    _send_admin_message
)
from src.handlers.x_handler import process_x
from src.services.proxy_service import load_proxies 
from utils.cache_storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from utils.runtime_state import is_running

load_dotenv()

semaphore = asyncio.Semaphore(3)

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)

async def main():

    if not is_running("x"):
        print("⛔ X mode STOP")
        return

    await init_telegram(os.getenv("TELEGRAM_TOKEN_SOCIAL"))

    try:
        await load_proxies()

    except Exception as e:

        msg = (
            f"🚨 Gagal load proxy\n"
            f"Error: {e}"
        )

        print(msg)

        await _send_admin_message(msg)

        await close_telegram()

        return
    
    asyncio.create_task(telegram_worker())

    cache = load_cache("x")

    TARGETS = load_targets()
    tasks = []
    
    for name, accounts in TARGETS.items():

        if not is_running("x"):
            print("⛔ X dihentikan")
            break

        tasks.append(
            process_x(
                name,
                accounts,
                cache,
                semaphore
            )
        )

    await asyncio.gather(*tasks)

    save_cache(cache, "x")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())