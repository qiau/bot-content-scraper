import os
import aiohttp
import json
from dotenv import load_dotenv

from src.utils.telegram_queue import enqueue

load_dotenv()

session = None
TOKEN = None
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

# =========================
# 🔥 INIT / CLOSE
# =========================
async def init_telegram(token):
    global session, TOKEN
    TOKEN = token
    session = aiohttp.ClientSession()

async def close_telegram():
    if session:
        await session.close()

# =========================
# 🔒 AUTH (buat nanti command)
# =========================
def is_admin(user_id: int):
    return str(user_id) == str(ADMIN_ID)


# =========================
# 🔵 INTERNAL SEND
# =========================
async def _post(method, payload):

    url = (
        f"https://api.telegram.org/"
        f"bot{TOKEN}/{method}"
    )

    async with session.post(
        url,
        data=payload
    ) as res:

        if res.status != 200:

            text = await res.text()

            print(
                f"❌ Telegram {method} error:",
                text
            )

# =========================
# 🔵 INTERNAL (REAL SENDER)
# =========================
async def _send_admin_message(text, parse_mode=None):

    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    await _post(
        "sendMessage",
        payload
    )

async def _send_message(text, parse_mode=None):

    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    await _post(
        "sendMessage",
        payload
    )

async def _send_photo(photo_url, caption=None, parse_mode=None):

    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption or ""
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    await _post(
        "sendPhoto",
        payload
    )

async def _send_video(video_url, caption=None, parse_mode=None):

    payload = {
        "chat_id": CHANNEL_ID,
        "video": video_url,
        "caption": caption or ""
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    await _post(
        "sendVideo",
        payload
    )

async def _send_media_group(media_group):
    MAX_MEDIA = 10

    for i in range(0, len(media_group), MAX_MEDIA):
        chunk = media_group[i:i + MAX_MEDIA]

        # caption hanya di album pertama
        if i != 0:
            for item in chunk:
                item.pop("caption", None)

        payload = {
            "chat_id": CHANNEL_ID,
            "media": json.dumps(chunk)
        }

        await _post(
            "sendMediaGroup",
            payload
        )

# =========================
# 🔵 PUBLIC (QUEUE WRAPPER)
# =========================

async def send_admin_message(text, parse_mode=None):
    await enqueue(_send_admin_message, text, parse_mode)

async def send_message(text, parse_mode=None):
    await enqueue(_send_message, text, parse_mode)

async def send_photo(photo_url, caption=None, parse_mode=None):
    await enqueue(_send_photo, photo_url, caption, parse_mode)

async def send_video(video_url, caption=None, parse_mode=None):
    await enqueue(_send_video, video_url, caption, parse_mode)

async def send_media_group(media_group):
    await enqueue(_send_media_group, media_group)