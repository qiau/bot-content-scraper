import asyncio
import re

async def get_tiktok_story(url):
    process = await asyncio.create_subprocess_exec(
        "python3",
        "-m",
        "gallery_dl",
        "--simulate",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    stdout, _ = await process.communicate()
    
    if not stdout:
        return []

    stories = []
    seen_ids = set()

    for line in stdout.decode(
        "utf-8",
        errors="ignore"
    ).splitlines():

        line = line.strip()

        if not line:
            continue

        if "TikTok audio" in line:
            continue

        match = re.search(
            r"#(\d{18,20})",
            line
        )

        if not match:
            continue

        story_id = match.group(1)

        if story_id in seen_ids:
            continue

        seen_ids.add(story_id)
        stories.append(story_id)

    stories.sort(key=int)

    return stories