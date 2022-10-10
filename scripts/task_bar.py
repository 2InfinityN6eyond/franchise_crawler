import tqdm
from multiprocessing import Process, Queue

class TaskBar(Process) :
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