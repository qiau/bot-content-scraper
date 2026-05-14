from html import escape
from src.utils.time_utils import format_wib_time

def sanitize_telegram_text(text):
    return (
        text
        .replace("@", "@\u200B")
        .replace("#", "#\u200B")
    )

def safe_text(text):
    return escape(
        sanitize_telegram_text(text)
    )

def format_instagram_caption(
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
            f"{safe_text(description)}"
            f"</blockquote>"
        )

    return (
        f"📸 <b>Instagram Update • "
        f"{escape(name)}</b>"
        f"{caption_text}\n\n"
        f"👤 <code>@{escape(username)}</code>\n"
        f"🗓 {date_text}\n\n"
        f'🔗 <a href="{link}">'
        f"Lihat postingan</a>"
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
            f"{safe_text(description)}"
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
            f"{safe_text(description)}"
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