import os
import re
import tempfile

COOKIE_DIR = "data/cookies"


def get_cookie_path(account_id):

    return (
        f"{COOKIE_DIR}/"
        f"cookies_{account_id}.txt"
    )


def normalize_cookie_text(text):

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # comment/header tetap
        if line.startswith("#"):

            lines.append(line)

            continue

        # split maksimal 7 field
        parts = re.split(
            r"\s+",
            line,
            maxsplit=6
        )

        # invalid row
        if len(parts) < 7:
            continue

        # convert jadi TAB-separated
        fixed_line = "\t".join(parts)

        lines.append(fixed_line)

    return "\n".join(lines)


def save_cookie(
    account_id,
    cookies_text
):

    os.makedirs(
        COOKIE_DIR,
        exist_ok=True
    )

    # =========================
    # 🔥 NORMALIZE COOKIE
    # =========================

    cookies_text = normalize_cookie_text(
        cookies_text
    )

    file_path = get_cookie_path(
        account_id
    )

    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        encoding="utf-8",
        dir=COOKIE_DIR
    ) as tmp:

        tmp.write(
            cookies_text.strip()
        )

        temp_name = tmp.name

    os.replace(
        temp_name,
        file_path
    )

    return file_path


def load_cookie(
    account_id
):

    file_path = get_cookie_path(
        account_id
    )

    if not os.path.exists(
        file_path
    ):
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()