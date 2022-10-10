import math
import requests
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import dateutil
from urllib.parse import urlparse, parse_qs
from multiprocessing import Process, Queue

#from scripts.franchise import Franchise
from franchise import Franchise


print_debug = print

class FranchiseDataProvideSystemCrawler(Process) :
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
        to_controller:Queue,
        from_controller:Queue,
        list_url:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/list.do",
        view_usl:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/view.do",
        max_concurrency:int = 40,
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

        return : None
        """

        super(FranchiseDataProvideSystemCrawler, self).__init__()

        self.from_controller = from_controller
        self.to_controller = to_controller

        self.list_url = list_url
        self.view_url = view_usl
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
        
        self.view_url_params = {

        }


    async def run_loop(self) :
        
        print_debug("entering run_loop")

        while True :
            if not self.from_controller.empty() :
                data = self.from_controller.get()
                if data["instruction"] == "fetch_list_url" :
                    self.fetchListUrlAndConstructFranchise(
                        list_size_of_list_url = data["list_size_of_list_url"],
                        page_index = data["page_index"]
                    )

                if data["instruction"] == "fetch_view_url" :
                    asyncio.ensure_future(
                        self.fetceViewUrlAndParse2Franchise(
                            franchise = data["franchise"]
                        )
                    )

                    print_debug(data)

            await asyncio.sleep(0.05)

    def run(self) :
        """
        override multiprocess.run()

        """
        asyncio.run(self.run_loop())

    def fetchListUrlAndConstructFranchise(
        self,
        list_url:str = None,
        view_url:str = None,
        list_size_of_list_url:int = 100,
        page_index:int = 0
    ) :
        """
        download html of list_url, extract view_url for each franchise,
        and call self.fetchFranciseView. 

        this is not concurrent. 

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

        try :

            resp = requests.get(
                list_url,
                params = url_query_param
            )

        except Exception as e :
            print("connection failed on list_url {}".format(
                list_url
            ))
            print("message:")
            print(e)

            self.to_controller.put({
                "status" : "error",
                "type" : "list_url",
                "params" : {
                    "list_size_of_list_url" : list_size_of_list_url,
                    "page_index" : page_index
                }
            })
            return

        try :
            soup = BeautifulSoup(resp.text.strip(), "lxml")

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
            print(e)
            
            self.to_controller.put({
                "status" : "error",
                "type"   : "list_url",
                "params" : {
                    "list_size_of_list_url" : list_size_of_list_url,
                    "page_index" : page_index
                }
            })

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

        print_debug("fetching_view")

        async with self.semaphore :
            try :
                async with aiohttp.ClientSession() as session :
                    async with session.get(franchise.url) as resp :
                        resp_text, resp_url = await resp.text(), resp.url

            except Exception as e :
                print("connection failed on {}".format(franchise.url))
                print("message :")
                print(e)

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
            print("failed to parse html from view_url {}".format(
                franchise.url
            ))
            print("message :")
            print(e)

            data = {
                "status" : "error",
                "type"   : "franchise",
                "franchise" : franchise
            }

        self.to_controller.put(data)