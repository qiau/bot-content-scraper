import aiohttp
import asyncio
from http.cookiejar import MozillaCookieJar
import traceback

def load_cookies(cookie_file):

    jar = MozillaCookieJar()

    jar.load(
        cookie_file,
        ignore_discard=True,
        ignore_expires=True
    )

    cookies = {}

    for cookie in jar:

        cookies[
            cookie.name
        ] = cookie.value

    return cookies

def build_headers():
    return {

        "User-Agent": (
            "Instagram 275.0.0.27.98 Android "
            "(33/13; 420dpi; 1080x2400; samsung; "
            "SM-G991B; o1s; exynos2100)"
        ),

        "Accept": "*/*",

        "Accept-Language": (
            "en-US,en;q=0.9"
        ),

        "X-IG-App-ID": (
            "936619743392459"
        )
    }

async def get_instagram_posts(username, user_id, session):
    
    feed_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/?count=3"

    try:      
        async with session.get(feed_url) as res:
        
            if res.status == 429:
                print(f"[IG] {username} ❌ rate limit (429)")
                return "rate_limit" 

            if res.status != 200:
                print(f"[IG] {username} ❌ feed status {res.status}")
                return "ig_error"

            try:
                feed_data = await res.json()

            except Exception:
                text = await res.text()

                print(
                    f"[IG] {username} ❌ invalid json feed"
                )

                print(text[:300])

                return "ig_error"

        items = feed_data.get("items", [])
        print(
            f"[IG] {username} total items: {len(items)}"
        )

        if not items:
            print(f"[IG] {username} ⚠️ feed kosong")
            return []

        results = []

        for item in items[:3]:
            shortcode = item.get("code")

            if not shortcode:
                continue

            media = []

            # =========================
            # 🔥 PRIORITAS: CAROUSEL
            # =========================
            carousel = item.get("carousel_media") or item.get("carousel_media_extended")

            if carousel:
                for m in carousel:
                    if m.get("video_versions"):
                        media.append({
                            "type": "video",
                            "url": m["video_versions"][0]["url"]
                        })
                    elif m.get("image_versions2"):
                        
                        candidates = (
                            m["image_versions2"]
                            .get("candidates", [])
                        )

                        if candidates:
                            media.append({
                                "type": "image",
                                "url": candidates[0]["url"]
                            })

            # =========================
            # 🎥 VIDEO
            # =========================
            elif item.get("video_versions"):
                media.append({
                    "type": "video",
                    "url": (
                        item["video_versions"][0]["url"]
                    )
                })

            # =========================
            # 🖼️ IMAGE
            # =========================
            elif item.get("image_versions2"):
        
                candidates = (
                    item["image_versions2"]
                    .get("candidates", [])
                )

                if candidates:
                    media.append({
                        "type": "image",
                        "url": candidates[0]["url"]
                    })

            if not media:
                continue

            results.append({
                "shortcode": shortcode,
                "media": media,
                "description": (
                    (item.get("caption") or {}).get("text") or ""
                ),
                "timestamp": (
                    item.get(
                        "taken_at"
                    )
                )
            })

        print(
            f"[IG] {username} "
            f"✔️ "
            f"{len(results)} posts"
        )

        return results

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError
    ) as e:
        print(
            f"[IG] {username} "
            f"❌ request error: {e}"
        )
        return "ig_error"

    except Exception as e:
        print(
            f"[IG] {username} "
            f"❌ unknown error: {e}"
        )

        traceback.print_exc()

        return "ig_error"