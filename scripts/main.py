import argparse
import asyncio
from email.policy import default
from multiprocessing import Queue

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

from franchise import Franchise
from franchise_crawler import FranchiseDataProvideSystemCrawler
from task_bar import TaskBar
from controller import Controller
from logger import Logger



if __name__ == "__main__" :

    parser = argparse.ArgumentParser(
        description = "가맹사업   파싱 및 DB 저장"
    )
    parser.add_argument(
        '--num_franchise',
        type = int,
        default = -1,
        help = "number of franchise to get information. Given 1(which is default), search every franchise)"
    )
    parser.add_argument(
        '--max_concurrency',
        type = int,
        default = 40,
        help = "maximum number of concurrent asynchronous execution"
    )
    parser.add_argument(
        '--num_fetch_on_list_url',
        type = int,
        default = 300,
        help = "number of"
    )

    args = parser.parse_args()


    print(args.num_franchise)
    print(args.max_concurrency)
    print(args.num_fetch_on_list_url)

    num_franchise_to_crawl = 10

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