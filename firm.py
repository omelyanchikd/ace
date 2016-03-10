import random


class Firm:
    def __init__(self, id):
        self.workers = set()
        self.id = id

    def work(self):
        print("Look, I am a cool firm with id", self.id)
        for worker in self.workers:
            print("I have a worker with id", worker.id)

    def add_worker(self, worker):
        worker.employer = self.id
        worker.salary = random.randint(100, 150)
        self.workers.add(worker)

    def remove_worker(self, worker):
        self.workers.clear(worker)
