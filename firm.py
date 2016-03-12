import random


class Firm:
    def __init__(self, id, algorithm):
        self.workers = set()
        self.id = id
        self.algorithm = algorithm

    def work(self):
        print("Hi, I am working with algorithm", self.algorithm.__class__.__name__)
        return self.algorithm.decide(self)

    def add_worker(self, worker):
        worker.employer = self.id
        worker.salary = random.randint(100, 150)
        self.workers.add(worker)

    def remove_worker(self, worker):
        self.workers.clear(worker)
