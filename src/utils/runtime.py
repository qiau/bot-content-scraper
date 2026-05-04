import os

IG_MODE_FILE = "data/runtime/ig_mode.txt"

def is_ig_running():
    try:
        with open(IG_MODE_FILE, "r") as f:
            return f.read().strip() == "running"
    except:
        return True

def set_ig_mode(mode: str):
    os.makedirs(os.path.dirname(IG_MODE_FILE), exist_ok=True)

    with open(IG_MODE_FILE, "w") as f:
        f.write(mode)