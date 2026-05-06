import aiohttp
import asyncio

def build_headers(ig_account):
    sessionid = ig_account.get("sessionid")
    csrftoken = ig_account.get("csrftoken")

    if not sessionid or not csrftoken:
        raise ValueError("Cookie IG kosong")
    
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.instagram.com/",
        "X-Requested-With": "XMLHttpRequest",
        "X-IG-App-ID": "936619743392459",
        "Cookie": (
            f"sessionid={sessionid}; "
            f"csrftoken={csrftoken};"
        )
    }

async def get_latest_posts(username, ig_account, proxy=None):

    try:
        headers = build_headers(ig_account)

    except Exception as e:
        print(f"[IG] {username} ❌ header error:", e)
        return "ig_error"
    
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:

            # =========================
            # 🔹 STEP 1: ambil user_id
            # =========================
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

            async with session.get(url, proxy=proxy) as res:
                if res.status != 200:
                    print(
                        f"[IG] {username} ❌ user info status {res.status}"
                    )

                    # proxy / rate limit
                    if res.status in [429, 502, 503, 504]:
                        return "proxy_error"

                    return "ig_error"

                try:
                    data = await res.json()

                except Exception:
                    text = await res.text()

                    print(
                        f"[IG] {username} ❌ invalid json user info"
                    )

                    print(text[:300])

                    return "ig_error"

            if data.get("status") != "ok":
                print(f"[IG] {username} ❌ user info error")
                return "ig_error"

            user = data.get("data", {}).get("user")

            if not user:
                return "ig_error"

            user_id = user.get("id")

            if not user_id:
                return "ig_error"

            # =========================
            # 🔹 STEP 2: ambil feed
            # =========================
            feed_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"

            async with session.get(feed_url, proxy=proxy) as res:
         
                if res.status != 200:
                    print(
                        f"[IG] {username} ❌ feed status {res.status}"
                    )

                    if res.status in [429, 502, 503, 504]:
                        return "proxy_error"

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
                    "media": media
                })

            print(f"[IG] {username} ✔️ ambil {len(results)} post")

            return results

    except (
        aiohttp.ClientProxyConnectionError,
        aiohttp.ClientConnectorError,
        asyncio.TimeoutError
    ) as e:

        print(f"[IG] {username} ❌ proxy error:", e)

        return "proxy_error"
    
    except Exception as e:
        print(f"[IG] {username} ❌ error:", e)
        return "ig_error"