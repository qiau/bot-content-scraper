import os
import instaloader

from dotenv import load_dotenv


load_dotenv()


L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False
)

L.load_session_from_file(
    os.getenv("INSTAGRAM_USERNAME"),
    "data/session/instagram.session"
)

print(
    "✅ Instaloader session loaded"
)