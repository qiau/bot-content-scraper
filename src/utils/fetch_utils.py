import random
import asyncio

def load_proxies():
    try:
        with open("data/proxy2.txt") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

PROXIES = load_proxies()

async def fetch(session, url):
    proxies = PROXIES.copy()
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