import json
from datetime import datetime

from handlers.telegram_handler import _send_message
from src.utils.caption import format_birthday_caption

def load_targets():
    with open("data/targets.json", "r") as f:
        return json.load(f)

def main():
    
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

        # cek apakah hari & bulan sama
        if (born.month, born.day) == (today.month, today.day):

            age = today.year - born.year

            caption = format_birthday_caption(
                name,
                age
            )

            _send_message(caption)

if __name__ == "__main__":
    main()