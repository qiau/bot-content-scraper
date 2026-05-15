import json
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from src.handlers.telegram_handler import init_telegram, close_telegram, _send_message
from src.utils.caption_utils import format_birthday_caption

load_dotenv()

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)

async def main():

    await init_telegram(os.getenv("TELEGRAM_TOKEN_SOCIAL"))

    targets = load_targets()

    today = datetime.now()

    for name, data in targets.items():

        birth_date = data.get("birth_date")

        if not birth_date:
            continue

        try:
            born = datetime.strptime(birth_date, "%Y-%m-%d")
        except:
            print(f"{name}: invalid birth_date")
            continue

        if (born.month, born.day) == (today.month, today.day):

            age = today.year - born.year

            caption = format_birthday_caption(
                name,
                age
            )

            try:

                await _send_message(
                    caption,
                    parse_mode="HTML"
                )
                await asyncio.sleep(5)

            except Exception as e:
                print(
                    f"❌ Birthday error "
                    f"{name}: {e}"
                )

    await close_telegram()

if __name__ == "__main__":
    asyncio.run(main())