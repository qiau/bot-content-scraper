import os
import aiohttp
import json
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

session = None


async def init_telegram():
    global session
    session = aiohttp.ClientSession()


async def close_telegram():
    await session.close()


# =========================
# 🔵 SEND TEXT
# =========================
async def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }

    try:
        async with session.post(url, data=payload):
            pass
    except Exception as e:
        print("Error kirim message:", e)


# =========================
# 🔵 SEND PHOTO
# =========================
async def send_photo(photo_url, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption or ""
    }

    try:
        async with session.post(url, data=payload):
            pass
    except Exception as e:
        print("Error kirim photo:", e)


# =========================
# 🔵 SEND VIDEO
# =========================
async def send_video(video_url, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"

    payload = {
        "chat_id": CHAT_ID,
        "video": video_url,
        "caption": caption or ""
    }

    try:
        async with session.post(url, data=payload):
            pass
    except Exception as e:
        print("Error kirim video:", e)


# =========================
# 🔵 SEND MEDIA GROUP (ALBUM)
# =========================
async def send_media_group(media_group):
    MAX_MEDIA = 10

    for i in range(0, len(media_group), MAX_MEDIA):
        chunk = media_group[i:i+MAX_MEDIA]

        # 🔥 caption hanya di album pertama
        if i != 0:
            for item in chunk:
                item.pop("caption", None)

        payload = {
            "chat_id": CHAT_ID,
            "media": json.dumps(chunk)
        }

        try:
            async with session.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup",
                data=payload
            ):
                pass
        except Exception as e:
            print("Error kirim album:", e)

        await asyncio.sleep(random.uniform(3,5))