import argparse
import asyncio
from email.policy import default
from multiprocessing import Queue

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)


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
        "--max_task_limit",
        type = int,
        default = 80,
        help = "maximum number of active task"
    )
    parser.add_argument(
        '--max_concurrency',
        type = int,
        default = 80,
        help = "maximum number of concurrent asynchronous execution"
    )
    parser.add_argument(
        '--list_size_of_list_url',
        type = int,
        default = 300,
        help = "number of"
    )
    parser.add_argument(
        "--verbose",
        action = 'store_true',
        help = "print franchise when parsed"
    )

    args = parser.parse_args()


    controller_2_task_bar_queue = Queue()
    task_bar = TaskBar(
        data_queue = controller_2_task_bar_queue,
        num_franchise = args.num_franchise
    )
    task_bar.start()

    controller = Controller(
        to_taskbar_queue = controller_2_task_bar_queue,
        to_database_queue = None,
        max_task_limit = args.max_task_limit,
        max_concurrency = args.max_concurrency,
        num_franchises_to_crawl = args.num_franchise,
        list_size_of_list_url = args.list_size_of_list_url,
        verbose = True if args.verbose else False
    )
    asyncio.run(controller.start())