import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

PROXY_API = {
    "x": os.getenv("PROXY_X"),
    "ig": os.getenv("PROXY_IG"),
}

PROXIES = {
    "x": [],
    "ig": [],
}


async def load_proxies(service: str):
    global PROXIES

    url = PROXY_API.get(service)

    if not url:
        print(f"❌ PROXY_{service.upper()} tidak ada")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                text = await res.text()

        proxies = []

        for line in text.splitlines():
            if not line.strip():
                continue

            try:
                ip, port, user, password = line.strip().split(":")
                proxy = f"http://{user}:{password}@{ip}:{port}"
                proxies.append(proxy)
            except:
                print(f"❌ Format salah: {line}")

        PROXIES[service] = proxies
        print(f"✅ Loaded {len(proxies)} proxies for {service}")

    except Exception as e:
        print(f"❌ Gagal load proxy {service}:", e)
        PROXIES[service] = []

9
def get_proxies(service: str):
    return PROXIES.get(service, [])