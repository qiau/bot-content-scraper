import os
import aiohttp
import json
from dotenv import load_dotenv

from src.utils.telegram_queue import enqueue

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

session = None

# =========================
# 🔥 INIT / CLOSE
# =========================
async def init_telegram():
    global session
    session = aiohttp.ClientSession()

async def close_telegram():
    await session.close()

# =========================
# 🔵 INTERNAL (REAL SENDER)
# =========================

async def _send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    async with session.post(url, data=payload):
        pass

async def _send_photo(photo_url, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption or ""
    }

    async with session.post(url, data=payload):
        pass

async def _send_video(video_url, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"

    payload = {
        "chat_id": CHAT_ID,
        "video": video_url,
        "caption": caption or ""
    }

    async with session.post(url, data=payload):
        pass

async def _send_media_group(media_group):
    MAX_MEDIA = 10

    for i in range(0, len(media_group), MAX_MEDIA):
        chunk = media_group[i:i+MAX_MEDIA]

        # caption hanya di album pertama
        if i != 0:
            for item in chunk:
                item.pop("caption", None)

        payload = {
            "chat_id": CHAT_ID,
            "media": json.dumps(chunk)
        }

        async with session.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup",
            data=payload
        ):
            pass

# =========================
# 🔵 PUBLIC (QUEUE WRAPPER)
# =========================

async def send_message(text):
    await enqueue(_send_message, text)

async def send_photo(photo_url, caption=None):
    await enqueue(_send_photo, photo_url, caption)

async def send_video(video_url, caption=None):
    await enqueue(_send_video, video_url, caption)

async def send_media_group(media_group):
    await enqueue(_send_media_group, media_group)