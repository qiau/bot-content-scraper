import yt_dlp
import asyncio
import aiohttp


# =========================
# 🔴 AMBIL VIDEO ID (yt_dlp)
# =========================
async def get_latest_tiktoks(username, limit=3):
    url = f"https://www.tiktok.com/@{username}"

    loop = asyncio.get_running_loop()

    def run_yt_dlp():
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "playlistend": limit,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                videos = []

                entries = info.get("entries") or []

                entries.sort(
                    key=lambda x: int(x.get("id", 0)),
                    reverse=True
                )

                videos = []

                for entry in entries[:limit]:
                    video_id = entry.get("id")

                    if video_id:
                        videos.append(video_id)

                return videos

        except Exception as e:
            print(f"Error ambil TikTok {username}:", e)
            return []

    return await loop.run_in_executor(None, run_yt_dlp)


# =========================
# 🔵 TIKTOK DOWNLOADER API
# =========================
async def get_tiktok_video_url(tiktok_url):
    api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"

    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as res:
                if res.status != 200:
                    return None

                data = await res.json()

                if not data.get("data"):
                    return None

                d = data["data"]

                if d.get("images"):
                    return {
                        "type": "image",
                        "data": d["images"]
                    }

                if d.get("play"):
                    return {
                        "type": "video",
                        "data": d["play"]
                    }

    except Exception as e:
        print(f"Downloader error: {e}")

    return None