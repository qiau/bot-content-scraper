import os
import aiohttp
import asyncio
from dotenv import load_dotenv

from src.handlers.telegram_handler import (
    init_telegram,
    _send_message,
    is_admin
)
from src.utils.runtime import set_ig_mode, is_ig_running
from src.bot.proxy_handler import handle_proxy_upload
from src.bot.state import set_state, get_state, clear_state

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
    document = message.get("document")

    # 🔒 AUTH
    if not user_id or not is_admin(user_id):
        return

    # =========================
    # COMMAND
    # =========================
    if text == "/start":
        await _send_message(
            "🤖 Bot siap\n\n"
            "/start_ig\n"
            "/stop_ig\n"
            "/status_ig\n"
            "/update_proxy_ig\n"
            "/update_proxy_x\n"
            "/cancel_proxy_update"
        )

    elif text == "/start_ig":
        if is_ig_running():
            return
        set_ig_mode("running")
        await _send_message("🟢 IG diaktifkan")

    elif text == "/stop_ig":
        if not is_ig_running():
            return
        set_ig_mode("stopped")
        await _send_message("🔴 IG dihentikan")

    elif text == "/status_ig":
        status = "🟢 RUNNING" if is_ig_running() else "🔴 STOPPED"
        await _send_message(f"Status: {status}")

    # =========================
    # PROXY COMMAND
    # =========================
    elif text == "/update_proxy_ig":
        set_state(user_id, "waiting_proxy_ig")
        await _send_message("📥 Silakan upload file proxy IG")

    elif text == "/update_proxy_x":
        set_state(user_id, "waiting_proxy_x")
        await _send_message("📥 Silakan upload file proxy X")

    elif text == "/cancel_proxy_update":
        if get_state(user_id):
            clear_state(user_id)
            await _send_message("❌ Update proxy dibatalkan")
        else:
            await _send_message("⚠️ Tidak ada proses update yang aktif")

    # =========================
    # HANDLE FILE UPLOAD
    # =========================
    if document:
        state = get_state(user_id)

        if not state:
            await _send_message("⚠️ Gunakan command dulu (/update_proxy_ig atau /update_proxy_x)")
            return
        
        file_id = document.get("file_id")

        if state == "waiting_proxy_ig":
            count = await handle_proxy_upload(file_id, "proxy_ig")
            await _send_message(f"✅ Proxy IG updated ({count} proxy)")

        elif state == "waiting_proxy_x":
            count = await handle_proxy_upload(file_id, "proxy_x")
            await _send_message(f"✅ Proxy X updated ({count} proxy)")

        clear_state(user_id)

# =========================
# 🔥 LONG POLLING LOOP
# =========================
async def run_bot():
    offset = 0

    async with aiohttp.ClientSession() as session:

        # 🔥 SKIP OLD UPDATES
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

            async with session.get(url) as res:
                data = await res.json()

            if data.get("result"):
                offset = data["result"][-1]["update_id"] + 1
                print(f"⏭ Skip old updates, offset = {offset}")

        except Exception as e:
            print("❌ Skip error:", e)

        # 🔁 LOOP
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


async def main():
    print("🤖 Telegram bot starting...")
    await init_telegram(TOKEN)
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())