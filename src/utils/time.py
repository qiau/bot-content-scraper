from datetime import datetime
from zoneinfo import ZoneInfo


def format_wib_time(timestamp):

    if not timestamp:
        return "-"

    dt = datetime.fromtimestamp(
        int(timestamp),
        tz=ZoneInfo("Asia/Jakarta")
    )

    return dt.strftime(
        "%d %b %Y • %H:%M WIB"
    )