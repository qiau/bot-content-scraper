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
from src.utils.config_manager import update_account_config, get_account_config

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN_ADMIN")

# =========================
# 🔥 HANDLE UPDATE
# =========================
async def handle_update(update):
    message = update.get("message")
    if not message:
        return

    text = message.get("text", "")
    cmd = text.lower()
    user_id = message.get("from", {}).get("id")

    # 🔒 AUTH
    if not user_id or not is_admin(user_id):
        return

    # =========================
    # COMMAND
    # =========================
    if cmd == "/start":
        await _send_message(
            "🤖 Bot siap\n\n"
            "/start_ig\n"
            "/stop_ig\n"
            "/status_ig\n"
            "/set_ig\n"
            "/get_ig"
        )

    elif cmd == "/start_ig":
        if is_ig_running():
            return
        set_ig_mode("running")
        await _send_message("🟢 IG diaktifkan")

    elif cmd == "/stop_ig":
        if not is_ig_running():
            return
        set_ig_mode("stopped")
        await _send_message("🔴 IG dihentikan")

    elif cmd == "/status_ig":
        status = "🟢 RUNNING" if is_ig_running() else "🔴 STOPPED"
        await _send_message(f"Status: {status}")

    elif cmd.startswith("/set_ig"):
        parts = text.split()

        if len(parts) != 4:
            await _send_message(
                "❌ Format salah\nContoh:\n/set_ig acc1 sessionid csrftoken"
            )
            return

        _, name, sessionid, csrftoken = parts

        ok = update_account_config(name, sessionid, csrftoken)

        if ok:
            await _send_message(f"✅ {name} berhasil diupdate")
        else:
            await _send_message(f"❌ Akun {name} tidak ditemukan")

    elif cmd.startswith("/get_ig"):
        parts = text.split()

        if len(parts) != 2:
            await _send_message("❌ Format salah: /get_ig acc1")
            return

        name = parts[1]
        acc = get_account_config(name)

        if not acc:
            await _send_message("❌ Akun tidak ditemukan")
            return

        msg = (
            f"📄 {name}\n"
            f"sessionid: {acc['sessionid'][:6]}...\n"
            f"csrftoken: {acc['csrftoken'][:6]}..."
        )

        await _send_message(msg)

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