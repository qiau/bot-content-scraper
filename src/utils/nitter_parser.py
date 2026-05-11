import re
import urllib.parse

def parse_media(item):
    # 🔥 ambil hanya tweet utama (hindari quote)
    main = item.split("<hr/>")[0]

    imgs = re.findall(r'https://nitter\.net/pic/[^\"]+', main)

    images = []
    has_video = False

    for url in imgs:

        decoded = urllib.parse.unquote(url.split("/pic/")[1])

        if any(x in decoded for x in [
            "video_thumb",
            "ext_tw_video_thumb",
            "amplify_video_thumb"
        ]):
            has_video = True
            continue

        if not decoded.startswith("media/"):
            continue

        real = f"https://pbs.twimg.com/{decoded}?name=orig"
        images.append(real)

    return images, has_video