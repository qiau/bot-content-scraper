import asyncio
import aiohttp
import os

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

if datetime.now().day >= 15:
    PROXY_APIS = [
        os.getenv("PROXY_2"),
        os.getenv("PROXY_1")
    ]

else:
    PROXY_APIS = [
        os.getenv("PROXY_1"),
        os.getenv("PROXY_2")
    ]

PROXIES = []

async def load_proxies():

    global PROXIES

    for proxy_api in PROXY_APIS:
        if not proxy_api:
            continue

        try:
            async with aiohttp.ClientSession() as session:

                async with session.get(proxy_api) as res:

                    text = await res.text()

            proxies = []

            for line in text.splitlines():

                line = line.strip()

                if not line:
                    continue

                try:
                    ip, port, user, password = (
                        line.split(":")
                    )

                    proxies.append(
                        f"http://{user}:{password}"
                        f"@{ip}:{port}"
                    )

                except ValueError:
                    print(
                        f"❌ Format salah: {line}"
                    )

            PROXIES = proxies

            print(
                f"✅ Loaded "
                f"{len(PROXIES)} proxies"
            )

            return

        except Exception as e:
            print(
                f"❌ Failed {proxy_api}: {e}"
            )
            print(
                "⏳ Retry proxy lain dalam 5 detik..."
            )

            await asyncio.sleep(5)

    PROXIES = []
    print("❌ Semua proxy API gagal")

def get_proxies():
    return PROXIES