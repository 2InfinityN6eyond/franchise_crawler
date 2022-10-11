import asyncio

async def worker():
    print("starting sleep")
    await asyncio.sleep(2)
    print("slept")

async def main():
    while True:
        asyncio.ensure_future(worker())
        await asyncio.sleep(0.01)

asyncio.run(main())