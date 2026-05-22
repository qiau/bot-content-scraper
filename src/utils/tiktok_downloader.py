import aiohttp
from html import unescape

async def extract_tiktok_data(tiktok_url):
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
                        "data": d["images"],
                        "create_time": d.get("create_time") or 0,
                        "description": unescape(
                            d.get("title", "")
                        ).strip()
                    }

                if d.get("play"):
                    return {
                        "type": "video",
                        "data": d["play"],
                        "create_time": d.get("create_time") or 0,
                        "description": unescape(
                            d.get("title", "")
                        ).strip()
                    }

    except Exception as e:
        print(f"Downloader error: {e}")

    return None