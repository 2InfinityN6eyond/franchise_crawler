from sys import int_info
import tqdm
from threading import Thread
from multiprocessing import Queue

class TaskBar(Thread) :
    """
    진행 상황을 시각적으로 표시한다.
    처음에 몇 개의 프렌차이즈를 크롤링할지 정해줘야 한다.

    다운로드받는 총 갯수가 바뀌는 상황에서는 아직은 구현 안됨.
    """


    def __init__(
        self,
        data_queue:Queue,
        num_franchise
    ) :
        super(TaskBar, self).__init__()

        self.data_queue = data_queue
        # 프로그램 시작시 cmd line 으로 입력한  크롤링할 가맹점 수
        # -1 을 입력하면 있는대로 탐색하는 것이기 때문에 -1이 들어올 수 있음.
        self.num_franchise = num_franchise

        # list_view 에서 가맹점 정보 테이블을 읽어오고,
        # 각 레코드에서 view_url을 알아낸 다음 크롤링함.
        
        # 현재까지 탐색한 list_view 갯수들 총합 
        self.num_list_url_searched = 0
        # 현재까지 list_view 들에서 알아낸 view_url 갯수들의 총함.
        self.num_view_url_to_search = 0

        # 현재까지 크롤링한 view_url 갯수
        self.num_view_url_searched = 0

    def run(self) :
        with tqdm.tqdm(total = self.num_franchise) as bar :
            while True :
                if not self.data_queue.empty() :
                    data = self.data_queue.get()
                    if (data["type"] == "num_view_url_to_search") :
                        self.num_view_url_to_search += data["num_view_url_to_search"]
                        bar.total = max(self.num_franchise, self.num_view_url_to_search)
                    
                    if (data["type"] == "view_url_parsed") :
                        bar.update(1)
                        #bar.set_description(data["view_url"])

    """
    def __init__(
        self,
        data_queue,
        num_task
    ) :
        super(TaskBar, self).__init__()
        self.data_queue = data_queue
        self.num_task = num_task

    def run(self) :
        for i in tqdm.tqdm(range(self.num_task)) :
            data = None
            while data is None :
                if not self.data_queue.empty() :
                    data = self.data_queue.get()
    """