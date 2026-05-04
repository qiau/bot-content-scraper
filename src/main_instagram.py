import json
import asyncio
import random
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    send_message,
    init_telegram,
    close_telegram,
)
from src.handlers.instagram_handler import process_instagram
from src.utils.storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime import set_ig_mode, is_ig_running

load_dotenv()

with open("data/targets.json", "r") as f:
    TARGETS = json.load(f)

def load_ig_accounts():
    accounts = []
    i = 1

    while True:
        session = os.getenv(f"IG_SESSIONID_{i}")
        csrf = os.getenv(f"IG_CSRFTOKEN_{i}")

        if not session or not csrf:
            break

        accounts.append({
            "sessionid": session,
            "csrftoken": csrf
        })

        i += 1

    if not accounts:
        raise ValueError("❌ Tidak ada IG account")

    return accounts

def load_proxies():
    with open("data/proxy_ig.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def chunk_targets(targets, n):
    items = list(targets.items())
    random.shuffle(items)
    return [items[i::n] for i in range(n)]

async def main():
    if not is_ig_running():
        print("⛔ IG mode STOP (skip run)")
        return
    
    await init_telegram(os.getenv("TELEGRAM_TOKEN_IG"))
    asyncio.create_task(telegram_worker())

    cache = load_cache("instagram")

    IG_ACCOUNTS = load_ig_accounts()
    PROXIES = load_proxies()

    if len(PROXIES) < len(IG_ACCOUNTS):
        raise ValueError("❌ Jumlah proxy harus >= jumlah akun IG")

    # 🔥 OPTIONAL: random proxy tiap run (aman)
    # random.shuffle(PROXIES)

    account_proxy_map = {
        i: PROXIES[i] for i in range(len(IG_ACCOUNTS))
    }

    chunks = chunk_targets(TARGETS, len(IG_ACCOUNTS))

    should_stop_after_run = False

    for i, chunk in enumerate(chunks):
        if not is_ig_running():
            print("⛔ Dihentikan sebelum mulai akun")
            break

        ig_account = IG_ACCOUNTS[i]
        proxy = account_proxy_map[i]

        print(f"🚀 IG Account {i+1} mulai ({len(chunk)} target)")
        print(f"🌐 Proxy: {proxy}")
        
        fail_count = 0
        counter = 0

        for name, accounts in chunk:
            if not is_ig_running():
                print("⛔ Dihentikan oleh Telegram")
                break

            result = await process_instagram(
                name,
                accounts,
                cache,
                ig_account,
                proxy=proxy
            )

            if result is None:
                fail_count += 1
            else:
                fail_count = 0
            
            if fail_count >= 2:
                msg = (
                    f"🚨 IG Account {i+1} ERROR!\n"
                    "Akun ini dilewati\n"
                    "⏳ Sistem akan dihentikan setelah semua akun selesai"
                )
                await send_message(msg)
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
        await send_message("⛔ IG dihentikan (berlaku untuk run berikutnya)")
        set_ig_mode("stopped")

    await telegram_queue.join()
    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())