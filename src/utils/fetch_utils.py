import random
import asyncio
from src.services.proxy_service import get_proxies

async def fetch(session, url):
    proxies = get_proxies().copy()
    random.shuffle(proxies)

    for proxy in proxies:
        try:
            await asyncio.sleep(random.uniform(1, 2))

            async with session.get(url, proxy=proxy, timeout=10) as res:
                return await res.text()

        except Exception:
            print(f"Proxy gagal: {proxy}")

    print("Semua proxy gagal")
    return None