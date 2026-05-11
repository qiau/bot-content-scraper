from html import escape
from utils.time_utils import format_wib_time

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
        f"📸 <b>Instagram Update • "
        f"{escape(name)}</b>\n\n"
        f"👤 <code>@{escape(username)}</code>\n"
        f"🗓 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f'Lihat postingan</a>'
    )


def format_tiktok_caption(
    name, 
    username,
    link,
    timestamp=None,
    description=None
):

    date_text = format_wib_time(
        timestamp
    )

    caption_text = ""

    if description:

        caption_text = (
            f"\n\n"
            f"<blockquote>"
            f"{escape(description)}"
            f"</blockquote>"
        )

    return (
        f"🎵 <b>TikTok Update • "
        f"{escape(name)}</b>"
        f"{caption_text}\n\n"
        f"👤 <code>@{escape(username)}</code>\n"
        f"🗓 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f"Lihat postingan</a>"
    )

def format_x_caption(
    name, 
    username,
    link,
    timestamp=None,
    description=None
):

    date_text = format_wib_time(
        timestamp
    )
    caption_text = ""

    if description:

        caption_text = (
            f"\n\n"
            f"<blockquote>"
            f"{escape(description)}"
            f"</blockquote>"
        )

    return (
        f"🐦 <b>X Update • "
        f"{escape(name)}</b>"
        f"{caption_text}\n\n"
        f"👤 <code>@{escape(username)}</code>\n"
        f"🗓 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f"Lihat postingan</a>"
    )

def format_birthday_caption(
    name,
    age
):

    return (
        f"🎂 <b>Birthday Alert</b>\n\n"
        f"🎉 Hari ini "
        f"<b>{escape(name)}</b> "
        f"berulang tahun yang ke-{age}!\n\n"
        f"💖 Jangan lupa kirim doa "
        f"dan ucapan terbaik kalian~"
    )