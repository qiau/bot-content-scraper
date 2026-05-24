import os

RUNTIME_DIR = "data/runtime"

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


def get_instagram_account_file():

    return os.path.join(
        RUNTIME_DIR,
        "instagram_account.txt"
    )


def get_next_instagram_account():

    os.makedirs(
        RUNTIME_DIR,
        exist_ok=True
    )

    account_file = (
        get_instagram_account_file()
    )

    # =====================
    # INIT
    # =====================

    if not os.path.exists(
        account_file
    ):

        with open(
            account_file,
            "w"
        ) as f:

            f.write("2")

        return "1"

    try:
        with open(
            account_file,
            "r"
        ) as f:

            current = (
                f.read()
                .strip()
            )

    except:
        current = "1"

    next_account = (
        "2"
        if current == "1"
        else "1"
    )

    with open(
        account_file,
        "w"
    ) as f:

        f.write(
            next_account
        )

    return current


def get_batch_file():

    return os.path.join(
        RUNTIME_DIR,
        "instagram_batch.txt"
    )

def get_next_instagram_batch(
    total_batches
):

    os.makedirs(
        RUNTIME_DIR,
        exist_ok=True
    )

    batch_file = (
        get_batch_file()
    )

    # =====================
    # INIT
    # =====================

    if not os.path.exists(
        batch_file
    ):

        with open(
            batch_file,
            "w"
        ) as f:

            f.write("2")

        return 1

    try:
        with open(
            batch_file,
            "r"
        ) as f:
            current = int(
                f.read().strip()
            )

    except:
        current = 1


    next_batch = current + 1

    if next_batch > total_batches:
        next_batch = 1

    with open(
        batch_file,
        "w"
    ) as f:
        f.write(
            str(next_batch)
        )
    return current