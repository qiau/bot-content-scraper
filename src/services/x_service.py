import aiohttp
import re
import random
import asyncio

from html import unescape
from email.utils import (
    parsedate_to_datetime
)

from src.utils.fetch_utils import fetch
from src.utils.parser_utils import parse_media

NITTER_INSTANCES = [
    "https://nitter.net"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/120 Safari/537.36"
    )
}

async def get_latest_tweets(username, limit=3):
    async with aiohttp.ClientSession(headers=HEADERS) as session:

        instances = NITTER_INSTANCES.copy()
        random.shuffle(instances)

        for base in instances:
            await asyncio.sleep(random.uniform(1, 2))

            url = f"{base}/{username}/rss"

            try:
                text = await fetch(session, url)

                if not text:
                    continue

                if "rss feed disabled" in text:
                    continue

                if "<item>" not in text:
                    continue

                items = text.split("<item>")[1:]
                results = []

                for item in items:
                    # skip retweet
                    if "RT by" in item:
                        continue
                    
                    # cek hanya media valid (hindari kutipan post)
                    main = item.split("<hr/>")[0]
                    if "<img" not in main:
                        continue

                    match = re.search(r"<link>(.*?)</link>", item)
                    if not match:
                        continue

                    link = match.group(1)
                    tweet_id = link.split("/")[-1].replace("#m", "")
                    tweet_url = f"https://x.com/{username}/status/{tweet_id}"
                    pub_match = re.search(
                        r"<pubDate>(.*?)</pubDate>",
                        item
                    )

                    timestamp = None
                    
                    if pub_match:
                        try:
                            dt = (parsedate_to_datetime(pub_match.group(1)))
                            timestamp = int(dt.timestamp())
                        except Exception:
                            pass

                    # ambil text tweet
                    tweet_text = ""

                    title_match = re.search(
                        r"<title>(.*?)</title>",
                        item,
                        re.S
                    )

                    if title_match:
                        tweet_text = unescape(
                            title_match.group(1)
                        ).strip()

                        tweet_text = re.sub(
                            r"^R to @.*?:\s*",
                            "",
                            tweet_text
                        )

                        if tweet_text == "Image":
                            tweet_text = ""

                    # 🔥 4. parse media
                    images, has_video = parse_media(item)

                    # 🔥 5. validasi final (hindari false positive)
                    if not images and not has_video:
                        continue

                    results.append({
                        "id": tweet_id,
                        "url": tweet_url,
                        "images": images,
                        "has_video": has_video,
                        "timestamp": timestamp,
                        "text": tweet_text
                    })

                    if len(results) >= limit:
                        break

                if results:
                    return results

            except Exception as e:
                print(f"Error {base}: {e}")

    return []