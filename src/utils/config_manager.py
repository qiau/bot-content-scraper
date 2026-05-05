import json
import os
import tempfile

CONFIG_PATH = "data/config.json"


def update_account_config(name, sessionid, csrftoken):
    try:
        # 🔒 basic validation
        if not name or not sessionid or not csrftoken:
            return False

        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        updated = False

        for acc in data.get("instagram_accounts", []):
            if acc.get("name") == name:
                acc["sessionid"] = sessionid
                acc["csrftoken"] = csrftoken
                updated = True
                break

        if not updated:
            return False

        # 🔥 SAFE WRITE (anti corrupt)
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            temp_name = tmp.name

        os.replace(temp_name, CONFIG_PATH)

        return True

    except Exception as e:
        print("❌ Update config error:", e)
        return False


def get_account_config(name):
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        for acc in data.get("instagram_accounts", []):
            if acc.get("name") == name:
                return acc

        return None

    except Exception as e:
        print("❌ Read config error:", e)
        return None