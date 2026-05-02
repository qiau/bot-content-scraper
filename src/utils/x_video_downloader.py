import yt_dlp

def extract_media_urls(tweet_url, expected_count=1):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": "b[ext=mp4]",
    }

    
    videos = []
    video_error = False
    failed_count = 0

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tweet_url, download=False)

            # 🔥 multi video support
            if "entries" in info:
                for e in info["entries"]:
                    url = e.get("url")
                    if url:
                        videos.append(url)

                total_found = len(info["entries"])
            else:
                url = info.get("url")
                if url:
                    videos.append(url)
                    total_found = 1
                else:
                    total_found = 0

            if len(videos) < total_found:
                video_error = True
                failed_count = total_found - len(videos)

    except Exception as e:
        print(f"yt-dlp error: {e}")
        video_error = True
        failed_count = expected_count

    return videos, video_error, failed_count