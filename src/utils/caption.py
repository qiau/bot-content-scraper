from html import escape
from src.utils.time import format_wib_time

def format_instagram_caption(
    name, 
    username,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"📸 <b>{escape(name)}</b>\n"
        f"👤 {escape(username)}\n\n"
        f"🕒 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f'Lihat postingan</a>'
    )


def format_tiktok_caption(
    name, 
    username,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"🎵 <b>{escape(name)}</b>\n"
        f"👤 {escape(username)}\n\n"
        f"🕒 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f'Lihat postingan</a>'
    )

def format_x_caption(
    name, 
    username,
    link,
    timestamp=None
):

    date_text = format_wib_time(
        timestamp
    )

    return (
        f"🐦 <b>{escape(name)}</b>\n"
        f"👤 {escape(username)}\n\n"
        f"🕒 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f'Lihat postingan</a>'
    )