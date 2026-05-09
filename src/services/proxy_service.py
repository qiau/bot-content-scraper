import aiohttp
import os

from dotenv import load_dotenv

load_dotenv()

PROXY_APIS = [
    os.getenv("PROXY_1"),
   # os.getenv("PROXY_2"),
]

PROXIES = []

async def load_proxies():

    global PROXIES
    all_proxies = []
    try:

        async with aiohttp.ClientSession() as session:

            for url in PROXY_APIS:

                if not url:
                    continue

                try:

                    async with session.get(url) as res:
                        text = await res.text()

                    for line in text.splitlines():

                        if not line.strip():
                            continue

                        try:

                            ip, port, user, password = (
                                line.strip().split(":")
                            )

                            proxy = (
                                f"http://"
                                f"{user}:{password}"
                                f"@{ip}:{port}"
                            )

                            all_proxies.append(
                                proxy
                            )

                        except:

                            print(
                                f"❌ Format salah: {line}"
                            )

                except Exception as e:

                    print(
                        f"❌ Gagal load {url}: {e}"
                    )

        PROXIES = all_proxies

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