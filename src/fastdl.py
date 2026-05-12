import asyncio

from datetime import datetime
from zoneinfo import ZoneInfo

from playwright.async_api import (
    async_playwright
)


# ====================================
# URL POST INSTAGRAM
# ====================================

POST_URL = (
    "https://www.instagram.com/"
    "p/DXylhBAxQkr/"
)


# ====================================
# AMBIL DATA FASTDL
# ====================================

async def get_post_data(
    page,
    post_url
):

    api_result = None

    api_event = asyncio.Event()

    async def handle_response(
        response
    ):

        nonlocal api_result

        if (
            "api-wh.fastdl.app/api/convert"
            not in response.url
        ):

            return

        try:

            data = await response.json()

            if isinstance(
                data,
                list
            ):

                api_result = data

                api_event.set()

        except:
            pass

    page.on(
        "response",
        handle_response
    )

    await page.goto(
        "https://fastdl.app/en",
        wait_until="domcontentloaded"
    )

    await page.fill(
        'input[type="text"]',
        post_url
    )

    await page.click(
        'button[type="submit"]'
    )

    try:

        await asyncio.wait_for(
            api_event.wait(),
            timeout=20
        )

    except asyncio.TimeoutError:

        print(
            "❌ Timeout ambil JSON"
        )

        return []

    return api_result or []


# ====================================
# MAIN
# ====================================

async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context()

        page = await context.new_page()

        # block resource tidak penting
        await page.route(
            "**/*",
            lambda route: (
                route.abort()
                if route.request.resource_type
                in [
                    "image",
                    "media",
                    "font"
                ]
                else route.continue_()
            )
        )

        posts = await get_post_data(
            page,
            POST_URL
        )

        await browser.close()

    # ====================================
    # PRINT HASIL
    # ====================================

    print("\n========================")
    print("HASIL")
    print("========================\n")

    for i, item in enumerate(
        posts,
        1
    ):

        meta = item.get(
            "meta",
            {}
        )

        caption = meta.get(
            "title"
        )

        username = meta.get(
            "username"
        )

        taken_at = meta.get(
            "taken_at"
        )

        upload_time = None

        if taken_at:

            upload_time = datetime.fromtimestamp(
                int(taken_at),
                ZoneInfo("Asia/Jakarta")
            )

        print(
            f"POST #{i}"
        )

        print(
            f"USERNAME : {username}"
        )

        print(
            f"UPLOAD   : {upload_time}"
        )

        print(
            f"\nCAPTION:\n{caption}\n"
        )

        print(
            "CDN URLS:"
        )

        for media in item.get(
            "url",
            []
        ):

            media_url = media.get(
                "url"
            )

            if media_url:

                print(
                    media_url
                )

        print(
            "\n========================\n"
        )


asyncio.run(main())