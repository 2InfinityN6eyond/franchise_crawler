import math
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import dateutil
from urllib.parse import urlparse, parse_qs

from requests import session

#from scripts.franchise import Franchise
from franchise import Franchise

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
        list_url:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/list.do",
        view_usl:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/view.do",
        max_concurrency:int = 40,
    ) -> None :
        """
        args :
            list_url : str
                가맹사업정보제공시스템에서 여러 가맹본부의 리스트를 보여주는 웹페이지 주소

            view_url : str
                가맹사업정보제공시스템에서 특정 가맹본부의 세부 정보를 보여주는 웹페이지 주소

            max_concurrency : int
                동시 비동기 실행 인스턴스 수 제한.

        return : None
        """
        self.list_url = list_url
        self.view_url = view_usl
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)

    async def fetch(
        self,
        num = -1,
        num_fetch_at_once = 200
    ) -> list :
        """
        crawling site and fetch html data from site.
        fetch html table, and extract information,

        args :
            num :
                number of franchise data to fetch.
                given -1, fetch every data available. -> not implemented yet

        return :
            list of Franchise object.
            Of length "num"
        """
        
        assert num > 0

        # 예를 들어, 1000개의 가맹점 정보를 파싱하려면, 
        # 먼저 list_url에 접속해 한번에 num_fetch_at_once 만큼의 리스트를 얻고,
        # 그 리스트에 있는 각 가맹점의 view_url을 찾아서 모두 방문한다.
        # list_url에 표시할 수 있는 리스트 수의 제한이 있을 수 있으므로, 그걸 num_fetch_at_once로 제한한다.
        times_to_fetch = math.ceil(num / num_fetch_at_once)

        franchise_lists = [
            self.fetchFranchiseList(params={
                "searchCondition" : "",
                "searchKeyword" : "",
                "column" : "brd",
                "selUpjong":"21",
                "selIndus" : "",
                "pageUnit" : str(num_fetch_at_once) if i < times_to_fetch - 1 else str(num % num_fetch_at_once),
                "pageIndex" : str(i) 
            })
            for i in range(times_to_fetch - 1)
        ]

        return await asyncio.gather(*franchise_lists)
    
    async def fetchFranchiseList(
        self,
        list_url:str = None,
        view_url:str = None,
        params:dict = None
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

            params : dict
                url query parameters 
                default : None

        return :
            list of Franchise object
        """

        if list_url is None :
            list_url = self.list_url
        if view_url is None :
            view_url = self.view_url

        async with self.semaphore :
            async with aiohttp.ClientSession() as session :
                async with session.get(
                    list_url,
                    params = params
                ) as resp :
                    resp_text = await resp.text()

        try :
            table_rows = BeautifulSoup(resp_text, "lxml").table.tbody.findAll("tr")
        except :
            print("invalid list_url html")
            return

        franchises = list(map(
            lambda row_tag : Franchise(
                num = row_tag.find("td").text.strip(),
                url = '?'.join([view_url, row_tag.find("a")["onclick"].split("'")[1].split("?")[-1]])
            ),
            table_rows
        ))


        franchises = [
            self.fetchFranchiseView(
                franchise = franciese
            )
            for franciese in franchises
        ]

        return await asyncio.gather(*franchises)
            
    async def fetchFranchiseView(
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
        async with self.semaphore :    
            async with aiohttp.ClientSession() as session :
                async with session.get(franchise.url) as resp :
                    resp_text = await resp.text()

        franchise.parseFromHtml(resp_text)
        return franchise