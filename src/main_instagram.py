import json
import asyncio
import random
import os
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    send_message,
    init_telegram,
    close_telegram, _send_message
)
from src.handlers.instagram_handler import process_instagram
from src.services.proxy_service import load_proxies, get_proxies  
from src.utils.storage import load_cache, save_cache
from src.utils.telegram_queue import telegram_worker, telegram_queue
from src.utils.runtime import set_ig_mode, is_ig_running

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
    if not is_ig_running():
        print("⛔ IG mode STOP (skip run)")
        return
    
    await init_telegram(os.getenv("TELEGRAM_TOKEN_IG"))

    try:
        await load_proxies("ig")
    except Exception as e:
        msg = f"🚨 Gagal ambil proxy IG\nError: {e}"
        print(msg)
        await _send_message(msg)
        await close_telegram()
        return

    PROXIES = get_proxies("ig")

    if not PROXIES:
        msg = "🚨 Proxy IG kosong / gagal di-load dari Webshare"
        print(msg)
        await _send_message(msg)
        await close_telegram()
        return
    
    asyncio.create_task(telegram_worker())

    cache = load_cache("instagram")
    TARGETS = load_targets()
    config = load_config()

    IG_ACCOUNTS = config.get("instagram_accounts", [])
    if not IG_ACCOUNTS:
        raise ValueError("❌ Tidak ada IG account")

    random.shuffle(PROXIES)

    account_proxy_map = {
        i: PROXIES[i % len(PROXIES)] for i in range(len(IG_ACCOUNTS))
    }

    chunks = chunk_targets(TARGETS, len(IG_ACCOUNTS))

    should_stop_after_run = False

    for i, chunk in enumerate(chunks):
        if not is_ig_running():
            print("⛔ Dihentikan sebelum mulai akun")
            break

        ig_account = IG_ACCOUNTS[i]
        proxy = account_proxy_map[i]

        print(f"🚀 {ig_account['name']} mulai ({len(chunk)} target)")
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
            
            # =========================
            # 🔥 PROXY ERROR DETECT
            # =========================
            if fail_count >= 2:
                msg = (
                    f"🚨 {ig_account['name']} ERROR\n"
                    f"Proxy: {proxy}\n"
                    "Proxy ditandai sebagai mati atau IG Error"
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