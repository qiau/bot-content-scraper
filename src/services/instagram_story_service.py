import aiohttp
import asyncio

async def get_instagram_story(
    username,
    user_id,
    session
):

    story_url = (
        "https://www.instagram.com/"
        f"api/v1/feed/reels_media/"
        f"?reel_ids={user_id}"
    )

    try:

        async with session.get(
            story_url
        ) as res:

            if res.status != 200:

                print(
                    f"[IG STORY] {username} "
                    f"❌ story status {res.status}"
                )

                return "ig_error"

            try:
                data = await res.json()

            except Exception:
                text = await res.text()

                print(
                    f"[IG STORY] {username} "
                    f"❌ invalid json"
                )

                print(text[:300])

                return "ig_error"

        reels = data.get(
            "reels",
            {}
        )

        reel = reels.get(
            str(user_id)
        )

        if not reel:
            print(
                f"[IG STORY] {username} "
                f"⚠️ no reel"
            )

            return []

        items = reel.get(
            "items",
            []
        )

        print(
            f"[IG STORY] {username} "
            f"total stories: {len(items)}"
        )

        if not items:
            print(
                f"[IG STORY] {username} "
                f"⚠️ no story"
            )

            return []

        results = []

        for item in items:
            if (
                item.get("media_share")
                or item.get("story_feed_media")
                or item.get("reshared_story_media_author")
            ):
                continue

            story_id = item.get("id")

            if not story_id:
                continue

            media = []

            # =========================
            # 🎥 VIDEO STORY
            # =========================

            if item.get(
                "video_versions"
            ):
                media.append({
                    "type": "video",
                    "url": (
                        item["video_versions"][0]["url"]
                    )
                })

            # =========================
            # 🖼️ IMAGE STORY
            # =========================

            elif item.get(
                "image_versions2"
            ):
                candidates = (
                    (
                        item.get(
                            "image_versions2"
                        )
                        or {}
                    )
                    .get(
                        "candidates",
                        []
                    )
                )

                if candidates:
                    media.append({
                        "type": "image",
                        "url": (
                            candidates[0]["url"]
                        )
                    })

            if not media:
                continue

            results.append({
                "story_id": str(
                    story_id
                ),
                "media": media,
                "timestamp": int(
                    item.get(
                        "taken_at",
                        0
                    )
                ),
            })

        print(
            f"[IG STORY] {username} "
            f"✔️ {len(results)} stories"
        )

        return results

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError
    ) as e:

        print(
            f"[IG STORY] {username} "
            f"❌ request error: {e}"
        )

        return "ig_error"

    except Exception as e:

        print(
            f"[IG STORY] {username} "
            f"❌ unknown error: {e}"
        )

        return "ig_error"