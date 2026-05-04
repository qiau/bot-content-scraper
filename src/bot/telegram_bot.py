import os
import aiohttp
import asyncio
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    send_message,
    is_admin
)
from src.utils.runtime import set_ig_mode, is_ig_running

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN_IG")

# =========================
# 🔥 HANDLE UPDATE
# =========================
async def handle_update(update):
    message = update.get("message")
    if not message:
        return

    text = message.get("text", "").lower()
    user_id = message.get("from", {}).get("id")

    # 🔒 AUTH
    if not user_id or not is_admin(user_id):
        return

    # =========================
    # COMMAND
    # =========================
    if text == "/start":
        await send_message(
            "🤖 Bot siap\n\n"
            "/start_ig\n"
            "/stop_ig\n"
            "/status_ig"
        )

    elif text == "/start_ig":
        if is_ig_running():
            return
        set_ig_mode("running")
        await send_message("🟢 IG diaktifkan")

    elif text == "/stop_ig":
        if not is_ig_running():
            return
        set_ig_mode("stopped")
        await send_message("🔴 IG dihentikan")

    elif text == "/status_ig":
        status = "🟢 RUNNING" if is_ig_running() else "🔴 STOPPED"
        await send_message(f"IG Status: {status}")


# =========================
# 🔥 LONG POLLING LOOP
# =========================
async def run_bot():
    offset = 0

    async with aiohttp.ClientSession() as session:
        # =========================
        # 🔥 SKIP OLD UPDATES
        # =========================
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

            async with session.get(url) as res:
                data = await res.json()

            if data.get("result"):
                offset = data["result"][-1]["update_id"] + 1
                print(f"⏭ Skip old updates, offset = {offset}")

        except Exception as e:
            print("❌ Skip error:", e)

        # =========================
        # 🔁 LOOP NORMAL
        # =========================
        while True:
            try:
                url = (
                    f"https://api.telegram.org/bot{TOKEN}/getUpdates"
                    f"?offset={offset}&timeout=30"
                )

                async with session.get(url) as res:
                    data = await res.json()

                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    try:
                        await handle_update(update)
                    except Exception as e:
                        print("❌ Handle error:", e)

            except Exception as e:
                print("❌ Bot error:", e)
                await asyncio.sleep(3)

# =========================
# 🔥 MAIN ENTRY
# =========================
async def main():
    print("🤖 Telegram bot starting...")
    await init_telegram(TOKEN)
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())