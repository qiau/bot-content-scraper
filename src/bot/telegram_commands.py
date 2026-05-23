from src.handlers.telegram_handler import (
    _send_admin_message,
    is_admin
)
from src.handlers.manual_instagram_handler import process_manual_instagram
from src.utils.cookie_manager import save_cookie, load_cookie
from src.utils.runtime_state import set_mode, is_running
from src.utils.target_manager import add_target, update_target

async def handle_update(update):
    message = update.get("message")
    if not message:
        return

    text = message.get("text", "")
    cmd = text.lower()
    user_id = message.get("from", {}).get("id")

    if not user_id or not is_admin(user_id):
        return

    if cmd == "/start":
        await _send_admin_message(
            "🤖 Bot siap\n\n"

            "Manual post:\n"
            "/ig\n\n"

            "/start_all\n"
            "/stop_all\n\n"

            "/start_instagram\n"
            "/stop_instagram\n"
            "/status_instagram\n\n"

            "/start_x\n"
            "/stop_x\n"
            "/status_x\n\n"

            "/start_tiktok\n"
            "/stop_tiktok\n"
            "/status_tiktok\n\n"

            "/set_ig\n"
            "/get_ig\n\n"
            
            "/add_target\n"
            "/set_target\n"
        )

    elif cmd.startswith("/ig"):
        parts = text.split(
            maxsplit=1
        )

        if len(parts) != 2:
            await _send_admin_message(
                "❌ Format:\n/ig URL"
            )
            return

        url = parts[1].strip()

        await process_manual_instagram(url)

    elif cmd == "/start_all":

        platforms = [
            "instagram",
            "x",
            "tiktok"
        ]

        started = []

        for platform in platforms:

            if not is_running(platform):

                set_mode(
                    platform,
                    "running"
                )

                started.append(
                    platform.upper()
                )

        if started:

            await _send_admin_message(
                "🟢 Semua service diaktifkan\n\n"
                + "\n".join(started)
            )

        else:

            await _send_admin_message(
                "⚠️ Semua service sudah berjalan"
            )

    elif cmd == "/stop_all":

        platforms = [
            "instagram",
            "x",
            "tiktok"
        ]

        stopped = []

        for platform in platforms:

            if is_running(platform):

                set_mode(
                    platform,
                    "stopped"
                )

                stopped.append(
                    platform.upper()
                )

        if stopped:

            await _send_admin_message(
                "🔴 Semua service dihentikan\n\n"
                + "\n".join(stopped)
            )

        else:

            await _send_admin_message(
                "⚠️ Semua service sudah berhenti"
            )

    elif cmd.startswith("/start_"):

        platform = cmd.replace("/start_", "")

        if is_running(platform):
            return

        set_mode(platform, "running")

        await _send_admin_message(
            f"🟢 {platform.upper()} diaktifkan"
        )

    elif cmd.startswith("/stop_"):

        platform = cmd.replace("/stop_", "")

        if not is_running(platform):
            return

        set_mode(platform, "stopped")

        await _send_admin_message(
            f"🔴 {platform.upper()} dihentikan"
        )

    elif cmd.startswith("/status_"):

        platform = cmd.replace("/status_", "")

        status = (
            "🟢 RUNNING"
            if is_running(platform)
            else "🔴 STOPPED"
        )

        await _send_admin_message(
            f"{platform.upper()} Status:\n{status}"
        )   

    elif cmd.startswith("/set_ig"):
        parts = text.split(
            maxsplit=2
        )

        if len(parts) != 3:
            await _send_admin_message(
                "❌ Format salah\n"
                "Contoh:\n"
                "/set_ig 1 <cookies>"
            )
            return

        _, account_id, cookies_text = parts

        if account_id not in (
            "1",
            "2"
        ):
            await _send_admin_message(
                "❌ Account hanya 1 atau 2"
            )
            return
        
        save_cookie(
            account_id,
            cookies_text
        )

        await _send_admin_message(
            f"✅ cookies_{account_id}.txt updated"
        )

    elif cmd.startswith("/get_ig"):
        parts = text.split()

        if len(parts) != 2:
            await _send_admin_message(
                "❌ Format salah\n"
                "Contoh:\n"
                "/get_ig 1"
            )
            return
        
        account_id = parts[1]
        cookies = load_cookie(
            account_id
        )

        if not cookies:
            await _send_admin_message(
                "❌ Cookies tidak ditemukan"
            )
            return

        await _send_admin_message(
            cookies[:3000]
        )
    
    elif cmd.startswith("/add_target"):

        parts = text.split()

        if len(parts) != 4:

            await _send_admin_message(
                "Format:\n"
                "/add_target Nama platform username"
            )

            return

        _, name, platform, username = parts

        add_target(
            name,
            platform,
            username
        )

        await _send_admin_message(
            f"✅ Target ditambahkan\n\n"
            f"{name}\n"
            f"{platform}: {username}"
        )

    elif cmd.startswith("/set_target"):

        parts = text.split()

        if len(parts) != 4:

            await _send_admin_message(
                "Format:\n"
                "/set_target Nama platform username_baru"
            )

            return

        _, name, platform, username = parts

        ok = update_target(
            name,
            platform,
            username
        )

        if ok:
            await _send_admin_message(
                f"✅ Target diupdate\n\n"
                f"{name}\n"
                f"{platform}: {username}"
            )

        else:
            await _send_admin_message(
                "❌ Member tidak ditemukan"
            )
