from franchise import Franchise
from franchise_data_fetcher import FranchiseDataProvideSystemCrawler
import asyncio

from multiprocessing import Queue

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

from task_bar import TaskBar


num_franchise_to_crawl = 100

crawler_to_task_bar_queue = Queue()

task_bar = TaskBar(
    data_queue = crawler_to_task_bar_queue,
    num_task = num_franchise_to_crawl
)
task_bar.start()

crawler = FranchiseDataProvideSystemCrawler(
    data_queue = crawler_to_task_bar_queue
)


loop = asyncio.get_event_loop()
result = loop.run_until_complete(
    crawler.fetch(
        num = num_franchise_to_crawl
    )
)
#result = asyncio.run(crawler.fetch(num=500))


#pp.pprint(result)
print(result)