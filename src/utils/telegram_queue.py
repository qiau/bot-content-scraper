import asyncio
import random
from src.utils.cache_failed_storage import update_failed_post

telegram_queue = asyncio.Queue()

async def telegram_worker():
    while True:
        func, args, failed_meta = (
            await telegram_queue.get()
        )

        try:
            success = await func(*args)
            if success is False and failed_meta:
                
                failed, username, post = (
                    failed_meta
                )

                update_failed_post(
                    failed,
                    username,
                    post
                )

        except Exception as e:
            print(
                "Telegram worker error:",
                e
            )

        await asyncio.sleep(random.uniform(3,5))
        telegram_queue.task_done()

async def enqueue(func, *args, failed_meta=None):
    await telegram_queue.put((func, args, failed_meta))