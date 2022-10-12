import asyncio


def printAsyncioInfo() :
    tasks = asyncio.all_tasks()
    num_whole_tasks = len(tasks)
    num_curr_tasks = len(list(filter(
        lambda task : not task.done(),
        tasks
    )))
    num_done_tasks = len(list(filter(
        lambda task : task.done(),
        tasks
    )))
    print(f"{num_whole_tasks} tasks total, {num_curr_tasks} acitve, {num_done_tasks} done")



async def worker():
    print("starting sleep")
    await asyncio.sleep(2)
    print("slept")

async def main():
    while True:
        asyncio.ensure_future(worker())
        await asyncio.sleep(0.01)

        printAsyncioInfo()

asyncio.run(main())