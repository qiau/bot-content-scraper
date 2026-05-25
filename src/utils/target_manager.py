import json
import os
import tempfile
import random
import math
import shutil

TARGETS_PATH = "data/targets.json"
SPLIT_DIR = "data/target_splits"

BATCH_SIZE = 10


def load_targets():

    with open(
        TARGETS_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_targets(data):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir="data"
    ) as tmp:

        json.dump(
            data,
            tmp,
            indent=2,
            ensure_ascii=False
        )

        temp_name = tmp.name

    os.replace(temp_name, TARGETS_PATH)

    rebuild_instagram_splits(
        data
    )

def rebuild_instagram_splits(
    data
):

    os.makedirs(
        SPLIT_DIR,
        exist_ok=True
    )

    # =====================
    # FILTER IG ONLY
    # =====================

    instagram_targets = {}

    for name, accounts in data.items():

        if accounts.get(
            "instagram"
        ):

            instagram_targets[
                name
            ] = accounts

    # =====================
    # SHUFFLE
    # =====================

    items = list(
        instagram_targets.items()
    )

    random.shuffle(items)

    # =====================
    # REMOVE OLD SPLITS
    # =====================

    if os.path.exists(
        SPLIT_DIR
    ):
        shutil.rmtree(
            SPLIT_DIR
        )

    os.makedirs(
        SPLIT_DIR,
        exist_ok=True
    )

    # =====================
    # CREATE NEW SPLITS
    # =====================

    total_batches = math.ceil(
        len(items) / BATCH_SIZE
    )

    for i in range(
        total_batches
    ):

        chunk = items[
            i * BATCH_SIZE:
            (i + 1) * BATCH_SIZE
        ]

        split_data = dict(
            chunk
        )

        file_path = (
            f"{SPLIT_DIR}/"
            f"targets_{i+1}.json"
        )

        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            encoding="utf-8",
            dir=SPLIT_DIR
        ) as tmp:

            json.dump(
                split_data,
                tmp,
                indent=2,
                ensure_ascii=False
            )

            temp_name = tmp.name

        os.replace(
            temp_name,
            file_path
        )

    print(
        f"✅ Rebuilt "
        f"{total_batches} IG splits"
    )

def add_target(name, platform, username):

    data = load_targets()

    if name not in data:
        data[name] = {}

    data[name][platform] = username

    save_targets(data)

    return True


def update_target(name, platform, username):

    data = load_targets()

    if name not in data:
        return False

    data[name][platform] = username

    save_targets(data)

    return True