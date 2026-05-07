import json
import os
import tempfile

TARGETS_PATH = "data/targets.json"


def load_targets():

    with open(
        TARGETS_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_targets(data):

    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8"
    ) as tmp:

        json.dump(
            data,
            tmp,
            indent=2,
            ensure_ascii=False
        )

        temp_name = tmp.name

    os.replace(temp_name, TARGETS_PATH)


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