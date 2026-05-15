from html import escape

MAX_TELEGRAM_TEXT = 900

def sanitize_telegram_text(text):
    return (
        text
        .replace("@", "@\u2060")
        .replace("#", "#\u2060")
    )


def trim_telegram_text(
    text,
    max_length=MAX_TELEGRAM_TEXT
):

    if len(text) <= max_length:
        return text

    return (
        text[:max_length - 3]
        + "..."
    )


def safe_text(text):
    text = trim_telegram_text(
        text
    )
    text = sanitize_telegram_text(
        text
    )
    return escape(text)