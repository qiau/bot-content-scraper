import os

RUNTIME_DIR = "data/runtime"


def get_mode_file(platform):
    return os.path.join(
        RUNTIME_DIR,
        f"{platform}_mode.txt"
    )


def is_running(platform):

    mode_file = get_mode_file(platform)

    try:
        with open(mode_file, "r") as f:
            return f.read().strip() == "running"

    except:
        return True


def set_mode(platform, mode):

    os.makedirs(RUNTIME_DIR, exist_ok=True)

    mode_file = get_mode_file(platform)

    with open(mode_file, "w") as f:
        f.write(mode)