import aiohttp
import os

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PROXY_API = (
    os.getenv("PROXY_2")
    if datetime.now().day >= 15
    else os.getenv("PROXY_1")
)

PROXIES = []


async def load_proxies():

    global PROXIES

    proxies = []

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(PROXY_API) as res:

                text = await res.text()

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

    except Exception as e:

        print(
            f"❌ Proxy load error: {e}"
        )

        PROXIES = []


def get_proxies():

    return PROXIES