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

        if func.__name__ == "_send_message":
            delay = random.uniform(3, 5)
        else:
            delay = random.uniform(10, 15)

        await asyncio.sleep(delay)
        telegram_queue.task_done()

async def enqueue(func, *args):
    await telegram_queue.put((func, args))