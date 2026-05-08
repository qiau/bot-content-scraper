from src.utils.time import format_wib_time


def format_instagram_caption(
    name,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"📸 <b>{name}</b>\n\n"
        f"🕒 {date_text}\n\n"
        f'<a href="{link}">Instagram</a>'
    )


def format_tiktok_caption(
    name,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"🎵 <b>{name}</b>\n\n"
        f"🕒 {date_text}\n\n"
        f'<a href="{link}">TikTok</a>'
    )

def format_x_caption(
    name,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"🐦 <b>{name}</b>\n\n"
        f"🕒 {date_text}\n\n"
        f'<a href="{link}">X</a>'
    )