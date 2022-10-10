from franchise import Franchise
from franchise_data_fetcher import FranchiseDataProvideSystemCrawler
import asyncio

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

crawler = FranchiseDataProvideSystemCrawler()

#loop = asyncio.get_event_loop()
#result = loop.run_until_complete(crawler.fetch(num = 5000))

result = asyncio.run(crawler.fetch(num=5000))

pp.pprint(result)


"""
async def fetch() :
    return await crawler.fetchFranchiseList(
        params = {
            "searchCondition" : "",
            "searchKeyword" : "",
            "column" : "brd",
            "selUpjong":"21",
            "selIndus" : "",
            "pageUnit" : "100",
            "pageIndex" : "1"
        }
)

loop = asyncio.get_event_loop()
result = loop.run_until_complete(fetch())

print(len(result))
print("___________")
print(result)
"""