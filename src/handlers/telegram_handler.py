import os
import aiohttp
import json
import asyncio
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

    for attempt in range(2):
        try:
            async with session.post(
                url,
                data=payload,
                timeout=60
            ) as res:

                if res.status == 200:
                    return True
                
                text = await res.text()
                print(
                    f"❌ Telegram "
                    f"{method} error "
                    f"[{res.status}]:",
                    text
                )
                if (
                    res.status == 429
                    and attempt == 0
                ):

                    try:

                        data = await res.json()

                        retry_after = (
                            data
                            .get("parameters", {})
                            .get("retry_after", 10)
                        )

                    except Exception:
                        retry_after = 10

                    print(
                        f"⏳ FloodWait "
                        f"{retry_after}s"
                    )

                    await asyncio.sleep(retry_after)
                    continue

                if (
                    res.status in
                    [500, 502, 503]
                    and attempt == 0
                ):
                    await asyncio.sleep(5)
                    continue

                return False

        except asyncio.TimeoutError:

            print(
                f"⚠️ Telegram "
                f"{method} timeout"
            )

            return None

        except Exception as e:

            print(
                f"⚠️ Telegram "
                f"{method} exception:",
                e
            )

            return None

    return False

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

    success = await _post(
        "sendMessage",
        payload
    )

    if success is False:
        await _send_admin_message(
            f"❌ Gagal mengirim pesan:\n{text}"
        )
    return success

async def _send_photo(photo_url, caption=None, parse_mode=None):

    payload = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption or ""
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    success = await _post(
        "sendPhoto",
        payload
    )

    if success is False:
        caption_text = (
            caption or ""
        )
        msg = (
            f"{caption_text}\n\n"
            f"⚠️ Preview gambar "
            f"gagal!\n"
            f'🔗 <a href="{photo_url}">'
            f"Download disini"
            f"</a>"
        )
        fallback_success = await _send_message(
            msg,
            parse_mode=parse_mode
        ) 

        await asyncio.sleep(2)

        await _send_admin_message(
            f"❌ Gagal mengirim foto:\n{photo_url}"
        )
        return fallback_success
    
    return success

async def _send_video(video_url, caption=None, parse_mode=None):

    payload = {
        "chat_id": CHANNEL_ID,
        "video": video_url,
        "caption": caption or ""
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    success = await _post(
        "sendVideo",
        payload
    )

    if success is False:

        caption_text = (
            caption or ""
        )

        msg = (
            f"{caption_text}\n\n"
            f"⚠️ Preview video "
            f"gagal!\n"
            f'🔗 <a href="{video_url}">'
            f"Download disini"
            f"</a>"
        )

        fallback_success = await _send_message(
            msg,
            parse_mode=parse_mode
        ) 

        await asyncio.sleep(2)

        await _send_admin_message(
            f"❌ Gagal mengirim video:\n{video_url}"
        )
        return fallback_success
    
    return success

async def _send_media_group(media_group):

    MAX_MEDIA = 10
    overall_success = True

    for i in range(0, len(media_group), MAX_MEDIA):
        chunk = media_group[i:i + MAX_MEDIA]

        if i != 0:
            for item in chunk:
                item.pop("caption", None)

        payload = {
            "chat_id": CHANNEL_ID,
            "media": json.dumps(chunk)
        }

        success = await _post(
            "sendMediaGroup",
            payload
        )

        if success is False:
            
            fallback_success = False

            photos = [
                x for x in chunk
                if x["type"] == "photo"
            ]

            videos = [
                x for x in chunk
                if x["type"] == "video"
            ]

            # =====================
            # PHOTO GROUP
            # =====================

            if photos:

                photo_success = await _post(
                    "sendMediaGroup",
                    {
                        "chat_id": CHANNEL_ID,
                        "media": json.dumps(
                            photos
                        )
                    }
                )
                if photo_success is True:
                    fallback_success = True

            # =====================
            # VIDEOS
            # =====================

            for idx, v in enumerate(videos):

                video_success = await _send_video(
                    v["media"],
                    caption=(
                        v.get("caption")
                        if not photos and idx == 0
                        else None
                    ),
                    parse_mode=(
                        v.get("parse_mode")
                        if not photos and idx == 0
                        else None
                    )
                )
                if video_success is True:
                    fallback_success = True

            await asyncio.sleep(2)

            await _send_admin_message(
                f"❌ Gagal mengirim media group"
            )
            if not fallback_success:
                overall_success = False
                
    return overall_success

# =========================
# 🔵 PUBLIC (QUEUE WRAPPER)
# =========================

async def send_admin_message(text, parse_mode=None):
    await enqueue(_send_admin_message, text, parse_mode)

async def send_message(text, parse_mode=None, failed_meta=None):
    await enqueue(_send_message, text, parse_mode, failed_meta=failed_meta)

async def send_photo(photo_url, caption=None, parse_mode=None, failed_meta=None):
    await enqueue(_send_photo, photo_url, caption, parse_mode, failed_meta=failed_meta)

async def send_video(video_url, caption=None, parse_mode=None, failed_meta=None):
    await enqueue(_send_video, video_url, caption, parse_mode, failed_meta=failed_meta)

async def send_media_group(media_group, failed_meta=None):
    await enqueue(_send_media_group, media_group, failed_meta=failed_meta)