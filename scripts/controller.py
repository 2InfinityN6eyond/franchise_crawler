from multiprocessing import Queue

from franchise import Franchise
from franchise_crawler import FranchiseDataProvideSystemCrawler
from logger import Logger

class Controller :
    """
    FranchiseDataProviderSystemCrawler를 이용해 크롤링을 진행하고,
    로깅, 테스크바 표시 등을 처리한다.
    메인 프로세스에서 작동시킨다.
    """
    def __init__(
        self,
        logger:Logger,
        controller_2_task_bar_queue:Queue,
        data_base_bridge        
    ) :
        pass
