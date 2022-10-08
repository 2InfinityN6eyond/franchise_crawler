import requests
from bs4 import BeautifulSoup
import asyncio
import dateutil


from scripts.francise import Francise

class FranciseDataFetcher :
    """
    
    """
    def __init__(
        self,
        base_url:str = "https://franchise.ftc.go.kr/mnu/00013/program/userRqst/list.do",
        max_concurrency:int = 100,
    ) :
        """
        
        """
        pass

        self.configs = [

        ]

    async def fetch(num = -1) :
        """
        crawling site and fetch html data from site.
        fetch html table, and extract information,

        args :
            num :
                number of francise data to fetch.

        return :
            list of Francise object.
            list is of length "num"
        """
        
        pass

    
    async def fetchTable(url) :
        """
        
        args :
            url :
                url of site

        return :
            list of Francise object
        """
        pass


    async def fetchFranciseData(url) :
        """

        args :
            url

        return :
            Francise object
        """
        resp = requests.get(url)

        francise = Francise(html = resp.text.strip())

        soup = BeautifulSoup(resp.content)
    

