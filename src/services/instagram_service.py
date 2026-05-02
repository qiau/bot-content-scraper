import aiohttp

def build_headers(ig_account):
    return {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.instagram.com/",
        "X-Requested-With": "XMLHttpRequest",
        "X-IG-App-ID": "936619743392459",
        "Cookie": f"sessionid={ig_account['sessionid']}; csrftoken={ig_account['csrftoken']};"
    }

async def get_latest_posts(username, ig_account):
    headers = build_headers(ig_account)

    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:

            # =========================
            # 🔹 STEP 1: ambil user_id
            # =========================
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

            async with session.get(url) as res:
                if res.status != 200:
                    print(f"[IG] {username} ❌ user info status {res.status}")
                    return None  
                
                data = await res.json()

            if data.get("status") != "ok":
                print(f"[IG] {username} ❌ user info error")
                return None

            user_id = data["data"]["user"]["id"]

            # =========================
            # 🔹 STEP 2: ambil feed
            # =========================
            feed_url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"

            async with session.get(feed_url) as res:
                if res.status != 200:
                    print(f"[IG] {username} ❌ feed status {res.status}")
                    return None
                
                feed_data = await res.json()

            items = feed_data.get("items", [])

            if not items:
                print(f"[IG] {username} ⚠️ feed kosong")
                return []

            results = []

            for item in items[:3]:
                shortcode = item.get("code")
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
                            media.append({
                                "type": "image",
                                "url": m["image_versions2"]["candidates"][0]["url"]
                            })

                # =========================
                # 🎥 VIDEO
                # =========================
                elif item.get("video_versions"):
                    media.append({
                        "type": "video",
                        "url": item["video_versions"][0]["url"]
                    })

                # =========================
                # 🖼️ IMAGE
                # =========================
                elif item.get("image_versions2"):
                    media.append({
                        "type": "image",
                        "url": item["image_versions2"]["candidates"][0]["url"]
                    })

                if not media:
                    continue

                results.append({
                    "shortcode": shortcode,
                    "media": media
                })

            print(f"[IG] {username} ✔️ ambil {len(results)} post")

            return results

    except Exception as e:
        print(f"[IG] {username} ❌ error:", e)
        return None