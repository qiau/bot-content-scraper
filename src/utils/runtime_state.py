import os
import time

RUNTIME_DIR = "data/runtime"

UPLOAD_STATE = {
    "mode": None,
    "expire": 0
}

def get_mode_file(platform):
    return os.path.join(
        RUNTIME_DIR,
        f"{platform}_runtime.txt"
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

def set_upload_mode(
    mode,
    duration
):

    UPLOAD_STATE["mode"] = mode

    UPLOAD_STATE["expire"] = (
        time.time() + duration
    )


def get_upload_mode():

    if (
        time.time()
        > UPLOAD_STATE["expire"]
    ):
        UPLOAD_STATE["mode"] = None
        return None

    return UPLOAD_STATE["mode"]

def clear_upload_mode():
    UPLOAD_STATE["mode"] = None
    UPLOAD_STATE["expire"] = 0