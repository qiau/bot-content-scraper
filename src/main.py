import json
import asyncio
import sys
import random
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    send_message,
    init_telegram,
    close_telegram,
)
from src.handlers.x_handler import process_x
from src.handlers.tiktok_handler import process_tiktok
from src.handlers.instagram_handler import process_instagram
from src.utils.storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue

load_dotenv()

with open("data/targets.json", "r") as f:
    TARGETS = json.load(f)

semaphore = asyncio.Semaphore(3)

# =========================
# 🔥 LOAD IG ACCOUNTS
# =========================
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
        raise ValueError("❌ Tidak ada IG account di .env")

    return accounts

# =========================
# 🔥 LOAD PROXIES
# =========================
def load_proxies():
    with open("data/proxy_ig.txt", "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

    if not proxies:
        raise ValueError("❌ Tidak ada proxy di proxy_ig.txt")

    return proxies

# =========================
# 🔥 SPLIT TARGETS
# =========================
def chunk_targets(targets, n):
    items = list(targets.items())
    random.shuffle(items)
    return [items[i::n] for i in range(n)]


# =========================
# MAIN
# =========================
async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None

    await init_telegram()
    asyncio.create_task(telegram_worker())

    # =========================
    # 🔥 INSTAGRAM MODE
    # =========================
    if mode == "instagram":
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

        for i, chunk in enumerate(chunks):
            ig_account = IG_ACCOUNTS[i]
            proxy = account_proxy_map[i]

            print(f"🚀 IG Account {i+1} mulai ({len(chunk)} target)")
            print(f"🌐 Proxy: {proxy}")

            fail_count = 0
            counter = 0

            for name, accounts in chunk:
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
                        "Kena limit / proxy bermasalah"
                    )
                    await send_message(msg)
                    break

                counter += 1

                # 🔥 BREAK PATTERN (anti bot)
                if counter % random.randint(4, 6) == 0:
                    sleep_time = random.uniform(120, 300)  # 2–5 menit
                    print(f"🛑 Cooldown panjang {sleep_time:.0f}s")
                    await asyncio.sleep(sleep_time)

                # 🔥 delay normal (lebih natural)
                await asyncio.sleep(random.uniform(35, 60))

            # 🔥 cooldown antar akun (WAJIB panjang)
            cooldown = random.uniform(300, 600)  # 5–10 menit
            print(f"😴 Cooldown antar akun {cooldown:.0f}s")
            await asyncio.sleep(cooldown)

        save_cache(cache, "instagram")

    # =========================
    # 🔥 X MODE
    # =========================
    elif mode == "x":
        cache = load_cache("x")

        tasks = [
            process_x(name, accounts, cache, semaphore)
            for name, accounts in TARGETS.items()
        ]

        if tasks:
            await asyncio.gather(*tasks)

        save_cache(cache, "x")

    # =========================
    # 🔥 TIKTOK MODE
    # =========================
    elif mode == "tiktok":
        cache = load_cache("tiktok")

        tasks = [
            process_tiktok(name, accounts, cache, semaphore)
            for name, accounts in TARGETS.items()
        ]

        if tasks:
            await asyncio.gather(*tasks)

        save_cache(cache, "tiktok")

    await telegram_queue.join()
    await close_telegram()


if __name__ == "__main__":
    asyncio.run(main())