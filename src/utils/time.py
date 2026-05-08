from datetime import datetime
from zoneinfo import ZoneInfo

DAYS = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

MONTHS = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}


def format_wib_time(timestamp):

    if not timestamp:
        return "-"

    dt = datetime.fromtimestamp(
        int(timestamp),
        tz=ZoneInfo("Asia/Jakarta")
    )

    day_name = DAYS[dt.weekday()]
    month_name = MONTHS[dt.month]

    return (
        f"{day_name}, "
        f"{dt.day} "
        f"{month_name} "
        f"{dt.year} | "
        f"{dt.strftime('%H:%M')} WIB"
    )