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
    
def load_config():
    with open("data/config.json", "r") as f:
        return json.load(f)

def chunk_targets(targets, n):
    items = list(targets.items())
    random.shuffle(items)
    return [items[i::n] for i in range(n)]

async def main():

    if not is_running("ig"):
        print("⛔ IG mode STOP (skip run)")
        return
    
    delay = random.randint(0, 3600) 
    await asyncio.sleep(delay)
    
    await init_telegram(os.getenv("TELEGRAM_TOKEN_IG"))
    
    asyncio.create_task(telegram_worker())

    cache = load_cache("instagram")
    TARGETS = load_targets()
    IG_ACCOUNTS = load_config()
  
    if not IG_ACCOUNTS:
        raise ValueError("❌ Tidak ada IG account")

    chunks = chunk_targets(TARGETS, len(IG_ACCOUNTS))

    should_stop_after_run = False

    for i, chunk in enumerate(chunks):
        if not is_running("ig"):
            print("⛔ Dihentikan sebelum mulai akun")
            break

        ig_account = IG_ACCOUNTS[i]

        print(f"🚀 {ig_account['name']} mulai ({len(chunk)} target)")
        
        fail_count = 0
        counter = 0

        for name, target in chunk:
            if not is_running("ig"):
                print("⛔ Dihentikan oleh Telegram")
                break

            result = await process_instagram(
                name,
                target,
                cache,
                ig_account,
                proxy=None
            )

            if result == "proxy_error":
                fail_count += 1

            elif result == "ig_error":
                # IG error tidak dianggap proxy mati
                print(f"⚠️ IG error pada {name}")

            else:
                fail_count = 0
            
            # =========================
            # 🔥 PROXY ERROR DETECT
            # =========================
            if fail_count >= 2:
                msg = (
                    f"🚨 {ig_account['name']} ERROR\n"
                    "Proxy ditandai sebagai mati atau IG Error"
                )
                await _send_admin_message(msg)
                should_stop_after_run = True
                break

            counter += 1

            # 🔥 BREAK PATTERN (anti bot)
            if counter % random.randint(4, 6) == 0:
                sleep_time = random.uniform(120, 300)  # 2–5 menit
                print(f"🛑 Cooldown panjang {sleep_time:.0f}s")
                await asyncio.sleep(sleep_time)

            # 🔥 delay normal (lebih natural)
            await asyncio.sleep(random.uniform(35, 60))

        cooldown = random.uniform(300, 600)  # 5–10 menit
        print(f"😴 Cooldown antar akun {cooldown:.0f}s")
        await asyncio.sleep(cooldown)

    save_cache(cache, "instagram")

    if should_stop_after_run:
        await _send_admin_message("⛔ IG dihentikan (berlaku untuk run berikutnya)")
        set_mode("ig","stopped")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())