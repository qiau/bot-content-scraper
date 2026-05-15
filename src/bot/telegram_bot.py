import os
import aiohttp
import asyncio
from dotenv import load_dotenv

from src.bot.telegram_commands import handle_update
from src.bot.telegram_documents import handle_document
from src.handlers.telegram_handler import init_telegram

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN_ADMIN")

async def run_bot():
    offset = 0

    async with aiohttp.ClientSession() as session:

        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

            async with session.get(url) as res:
                data = await res.json()

            if data.get("result"):
                offset = data["result"][-1]["update_id"] + 1
                print(f"⏭ Skip old updates, offset = {offset}")

        except Exception as e:
            print("❌ Skip error:", e)

        while True:
            try:
                url = (
                    f"https://api.telegram.org/bot{TOKEN}/getUpdates"
                    f"?offset={offset}&timeout=30"
                )

                async with session.get(url) as res:
                    data = await res.json()

                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    try:
                        await handle_update(update)
                        await handle_document(update, session, TOKEN)
                    except Exception as e:
                        print("❌ Handle error:", e)

            except Exception as e:
                print("❌ Bot error:", e)
                await asyncio.sleep(5)


async def main():
    print("🤖 Telegram bot starting...")
    await init_telegram(TOKEN)
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())