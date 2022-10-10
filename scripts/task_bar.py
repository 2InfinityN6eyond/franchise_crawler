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