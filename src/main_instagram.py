import json
import asyncio
import random
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    _send_admin_message,
    init_telegram,
    close_telegram
)
from src.handlers.instagram_handler import process_instagram
from src.utils.cache_storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime_state import set_mode, is_running

load_dotenv()

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)
    
async def main():

    if not is_running("instagram"):
        print("⛔ IG mode STOP (skip run)")
        return
    
    delay = random.randint(0, 3) 
    await asyncio.sleep(delay)
    
    await init_telegram(os.getenv("TELEGRAM_TOKEN_IG"))
    
    asyncio.create_task(telegram_worker())

    cache = load_cache("instagram")
    targets = load_targets()

    counter = 0
    
    for name, accounts in (
        targets.items()
    ):

        # stop from telegram
        if not is_running(
            "instagram"
        ):

            print(
                "⛔ Dihentikan"
            )

            break

        instagram_user = (
            accounts.get(
                "instagram"
            )
        )

        if not instagram_user:
            continue

        print(
            f"📸 Checking "
            f"{instagram_user}"
        )

        try:

            await process_instagram(
                name,
                accounts,
                cache
            )

        except Exception as e:

            await _send_admin_message(
                f"IG error "
                f"{instagram_user}: {e}"
            )

        counter += 1

        # =====================
        # LONG BREAK
        # =====================

        if counter % random.randint(8, 12) == 0:

            cooldown = random.uniform(
                180,
                420
            )

            print(
                f"😴 Long cooldown "
                f"{cooldown:.0f}s"
            )

            await asyncio.sleep(
                cooldown
            )

        # =====================
        # NORMAL DELAY
        # =====================

        else:

            delay = random.uniform(
                25,
                60
            )

            await asyncio.sleep(
                delay
            )

    save_cache(cache, "instagram")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())