import asyncio
import random

telegram_queue = asyncio.Queue()

async def telegram_worker():
    while True:
        func, args = await telegram_queue.get()

        try:
            await func(*args)
        except Exception as e:
            print("Telegram error:", e)

        await asyncio.sleep(random.uniform(15,20))
        telegram_queue.task_done()

async def enqueue(func, *args):
    await telegram_queue.put((func, args))