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

load_dotenv()

with open("data/targets.json", "r") as f:
    TARGETS = json.load(f)

semaphore = asyncio.Semaphore(3)

# =========================
# 🔥 LOAD IG ACCOUNTS (DYNAMIC)
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
    cache = load_cache()

    await init_telegram()

    if mode == "instagram":

        IG_ACCOUNTS = load_ig_accounts()
        chunks = chunk_targets(TARGETS, len(IG_ACCOUNTS))

        for i, chunk in enumerate(chunks):
            ig_account = IG_ACCOUNTS[i]

            print(f"🚀 IG Account {i+1} mulai ({len(chunk)} target)")

            fail_count = 0

            for name, accounts in chunk:
                result = await process_instagram(
                    name,
                    accounts,
                    cache,
                    ig_account
                )

                if result is None:
                    fail_count += 1
                else:
                    fail_count = 0

                if fail_count >= 2:
                    msg = (
                        f"🚨 IG Account {i+1} ERROR!\n"
                        "Cek session / cookies sekarang"
                    )
                    await send_message(msg)
                    break

                # 🔥 delay antar user (natural)
                await asyncio.sleep(random.uniform(10, 15))

            # 🔥 cooldown antar akun (PENTING)
            await asyncio.sleep(random.uniform(20, 40))

    else:
        tasks = []

        for name, accounts in TARGETS.items():
            if mode == "x":
                tasks.append(process_x(name, accounts, cache, semaphore))

            elif mode == "tiktok":
                tasks.append(process_tiktok(name, accounts, cache, semaphore))

        if tasks:
            await asyncio.gather(*tasks)

    await close_telegram()
    save_cache(cache)

if __name__ == "__main__":
    asyncio.run(main())