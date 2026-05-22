import aiohttp
from html import unescape

async def extract_tiktok_data(tiktok_url):
    api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"

    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return None

                result = await response.json()

    except Exception as e:
        print(f"TikWM error: {e}")
        return None
    
    data = result.get("data")

    if not data:
        return None

    media_type = None
    media_data = None

    if data.get("images"):
        media_type = "image"
        media_data = data["images"]

    elif data.get("play"):
        media_type = "video"
        media_data = data["play"]

    if not media_type:
        return None

    return {
        "type": media_type,
        "data": media_data,
        "create_time": (
            data.get("create_time")
            or 0
        ),
        "description": unescape(
            data.get("title", "")
        ).strip()
    }