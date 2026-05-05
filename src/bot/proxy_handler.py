import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN_IG")
CONFIG_PATH = "data/config.json"


# =========================
# 🔥 CONFIG HELPER
# =========================
def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


# =========================
# 🔥 MAIN HANDLER
# =========================
async def handle_proxy_upload(file_id, proxy_type):
    # 1. Ambil file dari Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.json()

        file_path = data["result"]["file_path"]

        download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

        async with session.get(download_url) as res:
            content = await res.text()

    # 2. Parse proxy
    proxies = []

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(":")

        # format: ip:port:user:pass
        if len(parts) == 4:
            ip, port, user, pwd = parts
            proxy = f"http://{user}:{pwd}@{ip}:{port}"
            proxies.append(proxy)

    # 3. Update config.json
    config = load_config()

    # pastikan key ada
    if proxy_type not in config:
        config[proxy_type] = []

    config[proxy_type] = proxies

    save_config(config)

    return len(proxies)