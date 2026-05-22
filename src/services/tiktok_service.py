import yt_dlp
import asyncio

async def get_tiktok_post(username, limit):
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

                entries = info.get("entries") or []

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