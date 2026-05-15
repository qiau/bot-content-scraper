from src.handlers.telegram_handler import (
    _send_admin_message,
    is_admin
)
from src.handlers.instagram_post_handler import process_instagram_post
from src.utils.runtime_state import set_mode, is_running, set_upload_mode
from src.utils.config_manager import update_account_config, get_account_config
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
            
            "/post\n"
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

            "/set_cookies\n"
            "/set_ig\n"
            "/get_ig\n\n"
            
            "/add_target\n"
            "/set_target\n"
        )

    elif cmd.startswith("/post"):
        parts = text.split(
            maxsplit=1
        )

        if len(parts) != 2:
            await _send_admin_message(
                "❌ Format:\n/post URL"
            )
            return

        url = parts[1].strip()

        await process_instagram_post(url)

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

    elif cmd == "/set_cookies":
        set_upload_mode("cookies", duration=600)

        await _send_admin_message(
            "📂 Upload file cookies.txt dalam 10 menit"
        )

    elif cmd.startswith("/set_ig"):
        parts = text.split()

        if len(parts) != 4:
            await _send_admin_message(
                "❌ Format salah\nContoh:\n/set_ig acc1 sessionid csrftoken"
            )
            return

        _, name, sessionid, csrftoken = parts

        ok = update_account_config(name, sessionid, csrftoken)

        if ok:
            await _send_admin_message(f"✅ {name} berhasil diupdate")
        else:
            await _send_admin_message(f"❌ Akun {name} tidak ditemukan")

    elif cmd.startswith("/get_ig"):
        parts = text.split()

        if len(parts) != 2:
            await _send_admin_message("❌ Format salah: /get_ig acc1")
            return

        name = parts[1]
        acc = get_account_config(name)

        if not acc:
            await _send_admin_message("❌ Akun tidak ditemukan")
            return

        msg = (
            f"📄 {name}\n"
            f"sessionid: {acc['sessionid'][:6]}...\n"
            f"csrftoken: {acc['csrftoken'][:6]}..."
        )

        await _send_admin_message(msg)
    
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
