import os

from src.handlers.telegram_handler import (
    is_admin,
    _send_admin_message
)
from src.utils.runtime_state import (
    get_upload_mode, clear_upload_mode
)

COOKIE_DIR = "data/cookies"

os.makedirs(
    COOKIE_DIR,
    exist_ok=True
)

async def handle_document(update, session, TOKEN):

    message = update.get("message")

    if not message:
        return

    # =====================
    # DOCUMENT
    # =====================

    document = message.get(
        "document"
    )

    if not document:
        return

    # =====================
    # ADMIN
    # =====================

    user_id = (
        message.get("from", {})
        .get("id")
    )

    if not is_admin(user_id):
        return

    # =====================
    # UPLOAD MODE
    # =====================

    mode = get_upload_mode()

    if not mode:
        return

    # =====================
    # FILE VALIDATION
    # =====================

    file_name = (
        document.get("file_name")
        or ""
    )

    if not file_name.endswith(
        ".txt"
    ):
        await _send_admin_message(
            "❌ File harus .txt"
        )
        return
    # =====================
    # FILE INFO
    # =====================

    file_id = document.get(
        "file_id"
    )

    # =====================
    # GET FILE PATH
    # =====================

    url = (
        f"https://api.telegram.org/"
        f"bot{TOKEN}/getFile"
    )

    async with session.get(
        url,
        params={
            "file_id": file_id
        }
    ) as res:

        data = await res.json()

    if not data.get("ok"):
        clear_upload_mode()
        await _send_admin_message(
            "❌ Gagal mengambil file"
        )

        return

    file_path = (
        data["result"]["file_path"]
    )

    # =====================
    # DOWNLOAD
    # =====================

    download_url = (
        f"https://api.telegram.org/file/"
        f"bot{TOKEN}/{file_path}"
    )

    async with session.get(
        download_url
    ) as res:

        content = await res.read()

    # =====================
    # SAVE PATH
    # =====================

    if mode == "cookies":
        save_path = os.path.join(
            COOKIE_DIR,
            "cookies.txt"
        )
    else:
        clear_upload_mode()
        await _send_admin_message(
            "❌ Upload mode tidak dikenal"
        )
        return

    with open(save_path, "wb") as f:
        f.write(content)

    # =====================
    # SUCCESS
    # =====================
    clear_upload_mode()
    await _send_admin_message(
        "✅ Cookies berhasil diperbarui"
    )