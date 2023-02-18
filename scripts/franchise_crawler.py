import math
import requests
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import dateutil
from urllib.parse import urlparse, parse_qs

from franchise import Franchise

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


print_debug = print

class FranchiseDataProvideSystemCrawler :
    """
    가맹사업정보제공시스템 웹페이지를 크롤링한다.

    가뱅사업정보제공시스템의 웹페이지는 두 가지로 구분되어 있다.
    1. 여러 가맹본부의 리스트를 보여주는 웹페이지    -> list_url 로 지칭
    2. 특정 가맹본부의 세부 정보를 보여주는 웹페이지 -> view_url 로 지칭

    FranchiseDateProvidesystemCrawler 는 먼저 list_url에 접속해 각 가맹본부들의 viwe_url을 찾는다.
    그 다음. view_url들에 접속해 각 가맹본부별 세부 정부를 파싱하고,
    가맹본부를 represent하는 Franchise 클래스에 정보를 저장햔다.

    동시에 여러 웹페이지의 html을 다운로드 받아야 하므로 asyncio를 통한 비동기 처리를 이용한다.
    """
    def __init__(
        self,
        to_controller,
        from_controller,
        list_url:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/list.do",
        view_url:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/view.do",
        max_concurrency:int = 40,
        max_task_limit:int = 100
    ) -> None :
        """
        args :

            data_queue : multiprocessing.Queue

            list_url : str
                가맹사업정보제공시스템에서 여러 가맹본부의 리스트를 보여주는 웹페이지 주소

            view_url : str
                가맹사업정보제공시스템에서 특정 가맹본부의 세부 정보를 보여주는 웹페이지 주소

            max_concurrency : int
                동시 비동기 실행 인스턴스 수 제한.

            max_task_limit : int

        return : None
        """

        self.from_controller = from_controller
        self.to_controller = to_controller

        self.list_url = list_url
        self.view_url = view_url
        self.max_task_limit = max_task_limit
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)

        self.list_url_params = {
            "searchCondition" : "",
            "searchKeyword" : "",
            "column" : "brd",
            "selUpjong": 21,
            "selIndus" : "",
            "pageUnit" : 0,
            "pageIndex" : 0
        }
        
        self.view_url_params = {}

        # controller 에서 요청을 보내는 족족 코푸틴을 실행시키다 보면 동시에 너무 많은 
        # 요청을 보내서, 처리시간이 늦어져 페이지 연결이 끊어질 확룔이 높아진다.
        # controller에서 요청을 보내면 우선 큐에 담고,
        # 현재 실행중인 task 갯수가 max_task_limit을 넘지 않도록 조절하며 실행시킨다.
        self.list_url_fetch_call_queue = []
        self.view_url_fetch_call_queue = []


    def step(self) :
        if not self.from_controller.empty() :
            data = self.from_controller.get()
            if data["instruction"] == "fetch_list_url" :        
                self.list_url_fetch_call_queue.append(data)

            if data["instruction"] == "fetch_view_url" :
                self.view_url_fetch_call_queue.append(data)

        if len(asyncio.all_tasks()) < self.max_task_limit :
            if len(self.list_url_fetch_call_queue) > 0 :
                data = self.list_url_fetch_call_queue.pop(0)
                asyncio.ensure_future(
                    self.fetchListUrlAndConstructFranchise(
                        list_size_of_list_url = data["list_size_of_list_url"],
                        page_index = data["page_index"]
                    )
                )
            if len(self.view_url_fetch_call_queue) > 0 :
                data = self.view_url_fetch_call_queue.pop(0)
                asyncio.ensure_future(
                    self.fetceViewUrlAndParse2Franchise(
                        franchise = data["franchise"]
                    )
                )


    '''
    async def run_loop(self) :
        #print_debug("entering run_loop")
        while True :
            if not self.from_controller.empty() :
                data = self.from_controller.get()
                if data["instruction"] == "fetch_list_url" :        
                    self.list_url_fetch_call_queue.append(data)

                if data["instruction"] == "fetch_view_url" :
                    self.view_url_fetch_call_queue.append(data)

            if len(asyncio.all_tasks()) < self.max_task_limit :
                if len(self.list_url_fetch_call_queue) > 0 :
                    data = self.list_url_fetch_call_queue.pop(0)
                    asyncio.ensure_future(
                        self.fetchListUrlAndConstructFranchise(
                            list_size_of_list_url = data["list_size_of_list_url"],
                            page_index = data["page_index"]
                        )
                    )
                if len(self.view_url_fetch_call_queue) > 0 :
                    data = self.view_url_fetch_call_queue.pop(0)
                    asyncio.ensure_future(
                        self.fetceViewUrlAndParse2Franchise(
                            franchise = data["franchise"]
                        )
                    )

            await asyncio.sleep(0.05)
    '''

    '''
    def run(self) :
        """
        override multiprocess.run()

        """
        asyncio.run(self.run_loop())
    '''

    async def fetchListUrlAndConstructFranchise(
        self,
        list_url:str = None,
        view_url:str = None,
        list_size_of_list_url:int = 100,
        page_index:int = 0
    ) :
        """
        download html of list_url, extract view_url for each franchise,
        and call self.fetchFranciseView. 

        args :
            list_url : str
                url of list_url.
                default : None.  This case, use self.list_url instead

            view_url : str
                url of view_url
                default : None. in this case,use self.view_url instead

        return :
            list of Franchise object
        """

        if list_url is None :
            list_url = self.list_url
        if view_url is None :
            view_url = self.view_url

        url_query_param = self.list_url_params.copy()
        url_query_param["pageUnit"] = list_size_of_list_url
        url_query_param["pageIndex"] = page_index


        async with self.semaphore :
            try :
                async with aiohttp.ClientSession() as session :
                    async with session.get(
                        list_url,
                        params = url_query_param
                    ) as resp :
                        resp_url = resp.url
                        resp_text = await resp.text()                
                """
                resp = requests.get(
                    list_url,
                    params = url_query_param
                )
                """

            except Exception as e :
                print("connection failed on list_url {}".format(
                    list_url
                ))
                print(f"message : {e}")

                # 원래는 controller에게 보고하고 끝내려 했지만,
                """
                self.to_controller.put({
                    "status" : "error",
                    "type" : "list_url",
                    "list_url" : resp_url
                })
                """
                # 구현이 뭔가 깔끔하지 못해서 그냥 자기 자신을 다시 call한다.
                print("retrying..")
                asyncio.ensure_future(
                    self.fetchListUrlAndConstructFranchise(
                        list_url = list_url,
                        view_url = view_url,
                        list_size_of_list_url = list_size_of_list_url,
                        page_index = page_index
                    )
                )
                
                return

        try :
            soup = BeautifulSoup(resp_text, "lxml")

            # check if page ends.
            if len(soup.findAll("div", "emptyNote")) > 0 :
                self.to_controller.put({
                    "status" : "end",
                    "type"   : "list_url"
                })
                return

            table_rows = soup.table.tbody.findAll("tr")
        except Exception as e :
            print("parse failed on url {}".format(resp.url))
            print(f"message : {e}")
            
            # 원래는 controller에게 보고한 뒤 끝내려 했지만,
            """
            self.to_controller.put({
                "status" : "error",
                "type"   : "list_url",
                "list_url" : resp_url
                #"params" : {
                #    "list_size_of_list_url" : list_size_of_list_url,
                #    "page_index" : page_index
                #}
            })
            """
            # 구현이 뭔가 깔끔하지 못해서 그냥 자기 자신을 다시 call한다.
            print("retrying..")
            asyncio.ensure_future(
                self.fetchListUrlAndConstructFranchise(
                    list_url = list_url,
                    view_url = view_url,
                    list_size_of_list_url = list_size_of_list_url,
                    page_index = page_index
                )
            )
            


            return

        # Franchise 를 construct할 때 에러가 발생하는 경우가 있는가?
        franchises = list(map(
            lambda row_tag : Franchise(
                num = row_tag.find("td").text.strip(),
                url = '?'.join([view_url, row_tag.find("a")["onclick"].split("'")[1].split("?")[-1]])
            ),
            table_rows
        ))

        self.to_controller.put({
            "status" : "success",
            "type"   : "list_url",
            "data"   : franchises
        })

    async def fetceViewUrlAndParse2Franchise(
        self,
        franchise:Franchise
    ) -> Franchise :
        """

        가맹사업정보제공시스템 웹페이지에서 

        args :
            
            franchise : Franchise
                
        return :
            Franchise object
        """
        """
        resp = await requests.get(
            view_url,
            params = params
        )
        """

        #print_debug("fetching_view")

        async with self.semaphore :
            try :
                async with aiohttp.ClientSession() as session :
                    async with session.get(franchise.url) as resp :
                        resp_text, resp_url = await resp.text(), resp.url

            except Exception as e :
                print("connection failed on {}".format(franchise.url))
                print(f"message : {e}")

                self.to_controller.put({
                    #"type" : "view_url",
                    "type" : "franchise",
                    "status" : "error",
                    "franchise" : franchise
                })

                return

        try : # html에 문제가 있어 파싱이 안될수도 있음
            franchise.parseFromHtml(resp_text)
            data = {
                "status" : "success",
                "type"   : "franchise",
                "franchise" : franchise
            }

        except Exception as e :
            franchise.parsing_succeed = False
            print("view_url parse failed : {}".format(
                franchise.url
            ))
            print(f"message : {e}")
            
            data = {
                "status" : "error",
                "type"   : "franchise",
                "franchise" : franchise
            }

        self.to_controller.put(data)