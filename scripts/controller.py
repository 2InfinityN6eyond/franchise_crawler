from multiprocessing import Process, Queue
from os import rename

from franchise import Franchise
#from franchise_crawler import FranchiseDataProvideSystemCrawler
from mp_franchise_crawler import FranchiseDataProvideSystemCrawler
from logger import Logger

print_debug = print

class Controller(Process) :
    """
    FranchiseDataProviderSystemCrawler를 이용해 크롤링을 진행하고,
    로깅, 테스크바 표시 등을 처리한다.
    메인 프로세스에서 작동시킨다.
    """
    def __init__(
        self,
        #logger:Logger,
        to_taskbar_queue:Queue,
        to_database_queue:Queue,
        #num_crawler:int,
        max_task_limit:int,
        max_concurrency:int,
        num_franchises_to_crawl:int,
        list_size_of_list_url:int,
        verbose:bool = False
    ) -> None :
        """
        # multiple crawlers are not implemented yet!

        # queue for communicate with crawlers.  required by crawler initializer.
        self.from_crawlers_queue = [Queue() for i in range(num_crawler)]
        self.to_crawlers_queue = [Queue() for i in range(num_crawler)]
        # initialize crawlers
        self.crawlers = list(map(
            lambda from_crawler, to_crawler : FranchiseDataProvideSystemCrawler(
                to_controller = from_crawler,
                from_controller = to_crawler,
                max_concurrency = max_concurrency
            ),
            self.from_crawlers_queue,
            self.to_crawlers_queue
        ))
        # start crawlers
        list(map(
            lambda crawler : crawler.start(),
            self.crawlers
        ))
        """

        super(Controller, self).__init__()

        self.to_taskbar_queue = to_taskbar_queue
        self.to_database_queue = to_database_queue
        
        self.num_franchises_to_crawl = num_franchises_to_crawl
        self.list_size_of_list_url = list_size_of_list_url
        self.num_view_url_searched = 0
        self.num_franchises_crawled = 0
        self.list_url_end_reached = False

        self.from_crwler_queue = Queue()
        self.to_crawler_queue = Queue()
        self.crawler = FranchiseDataProvideSystemCrawler(
            to_controller = self.from_crwler_queue,
            from_controller = self.to_crawler_queue,
            max_task_limit = max_task_limit,
            max_concurrency = max_concurrency
        )
        self.crawler.start()

        # list_url 웹페이지를 불러오기 실패할 경우.
        # 그러한 경우 url 스트링을 저장했다가 이후에 다시 요청한다.
        self.list_urls_failed_to_parse = []

        # view_url 웹페이지 파싱에 실패할 경우,
        # 자신의 view_url을 담고 있는 Franchise 인스턴스를 저장했다가
        # 이후에 다시 요청한다.
        self.franchises_failed_to_parse = []
        self.franchises = []

        self.verbose = verbose

    def run(self) :

        self.fetchListUrl()

        while True :
            if not self.from_crwler_queue.empty() :
                data = self.from_crwler_queue.get()

                if data["type"] == "list_url" :
                    if data["status"] == "success" :
                        
                        # data["data"] 는 Franchise의 인스턴스들의 리스트이다.
                        # 각 인스턴스에는 view_url이 저장되어 있다. 
                        self.fetchViewUrlAndParse2Franchise(data["data"])
                        
                        # generator로 개선할 여지가 많음
                        # self.list_size_of_list_url 만큼 읽었으므로
                        self.num_view_url_searched += self.list_size_of_list_url
                        self.fetchListUrl()

                        self.to_taskbar_queue.put({
                            "type" : "num_view_url_to_search",
                            "num_view_url_to_search" : len(data["data"])
                        })

                    elif data["status"] == "error" :
                        pass
                        #self.list_urls_failed_to_parse.append(
                        #    data["list_url"]
                        #)
                        pass

                    elif data["status"] == "end" :
                        # generator로 개선할 여지가 많음
                        self.list_url_end_reached = True

                    else :
                        print("controller got unknown message")
                        print(data)      

                elif data["type"] == "view_url" :
                    if data["status"] == "success" :
                        pass
                    elif data["status"] == "error" :
                        pass
                    else :
                        print("controller got unknown message")
                        print(data)

                elif data["type"] == "franchise" :
                    if data["status"] == "success" :
                        self.franchises.append(data["franchise"])

                        self.to_taskbar_queue.put({
                            "type" : "view_url_parsed",
                            "view_url" : data["franchise"].url
                        })

                        if self.verbose :
                            print(data["franchise"])
                    elif data["status"] == "error" :
                        # crawler가 franchise object에 저장된 
                        # self.franchises_failed_to_parse.append(data["franchise"])
                        
                        # 그냥 재시도한다.
                        self.fetchViewUrlAndParse2Franchise(
                            franchises=[data["franchise"]]
                        )

                    else :
                        print("controller got unknown message")
                        print(data)

                else :
                    print("controller got unknown message")
                    print(data)
 
 
    def fetchListUrl(self) :
        """
        balance work, send data to crawler
        """
        
        if self.list_url_end_reached :
            return

        page_index = 1 + self.num_view_url_searched // self.list_size_of_list_url

        self.to_crawler_queue.put(
            {
                "instruction" : "fetch_list_url",
                "list_size_of_list_url" : self.list_size_of_list_url,
                "page_index" : page_index
            }
        )

        if (
            self.num_view_url_searched >= self.num_franchises_to_crawl \
                and self.num_franchises_to_crawl > -1 
         ) :
            self.list_url_end_reached = True

    def fetchViewUrlAndParse2Franchise(self,franchises:list) :
        """
        # 리턴받은 franchise 인스턴스들에 대해
                        # FranchiseDataProvideSystemCrawler.fetceViewUrlAndParse2Franchise()
                        # 를 호출하도록 데이터를 전송한다.
                        list(map(
                            lambda franchise : self.to_crawler_queue.put({
                                "instruction" : "fetch_view_url",
                                "franchise"   : franchise
                            }),
                            data["data"]
                        ))
        """

        if not isinstance(franchises, list) :
            franchises = [franchises]
        list(map(
            lambda franchise : self.to_crawler_queue.put({
                "instruction" : "fetch_view_url",
                "franchise"   : franchise
            }),
            franchises
        ))
