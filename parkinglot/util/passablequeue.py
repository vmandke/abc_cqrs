import multiprocessing as mp

class MultiProcessPassableQueue():
    def __init__(self):
        self.producer_conn, self.consumer_conn = mp.Pipe(True)

    def get_producer_conn(self):
        return self.producer_conn

    def get_consumer_conn(self):
        return self.consumer_conn