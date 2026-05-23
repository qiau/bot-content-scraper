import asyncio
import instaloader
import random

from src.services.instagram_loader import L


async def get_latest_posts(
    username
):
    await asyncio.sleep(
        random.uniform(5, 8)
    )

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        None,
        scrape_posts,
        username
    )


def scrape_posts(username):

    try:

        profile = (
            instaloader.Profile
            .from_username(
                L.context,
                username
            )
        )

        results = []

        for i, post in enumerate(
            profile.get_posts()
        ):

            if i >= 3:
                break

            media = []

            # =====================
            # CAROUSEL
            # =====================

            if post.typename == (
                "GraphSidecar"
            ):

                for node in (
                    post.get_sidecar_nodes()
                ):

                    # VIDEO
                    if node.is_video:

                        media.append({
                            "type": "video",
                            "url": (
                                node.video_url
                            )
                        })

                    # IMAGE
                    else:

                        media.append({
                            "type": "image",
                            "url": (
                                node.display_url
                            )
                        })

            # =====================
            # SINGLE VIDEO
            # =====================

            elif post.is_video:

                media.append({
                    "type": "video",
                    "url": post.video_url
                })

            # =====================
            # SINGLE IMAGE
            # =====================

            else:

                media.append({
                    "type": "image",
                    "url": (
                        post.url
                    )
                })

            results.append({
                "shortcode": (
                    post.shortcode
                ),

                "timestamp": int(
                    post.date_utc.timestamp()
                ),

                "description": (
                    post.caption
                    or ""
                ),

                "media": media
            })

        print(
            f"[IG] {username} "
            f"✅ {len(results)} post"
        )

        return results

    except Exception as e:

        print(
            f"[IG] {username} "
            f"❌ error: {e}"
        )

        return []