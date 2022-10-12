import asyncio


async def work(sem):
    async with sem:
        print('working')
        await asyncio.sleep(1)

async def main():
    sem = asyncio.Semaphore(2)
    await asyncio.gather(work(sem), work(sem), work(sem))

asyncio.run(main())