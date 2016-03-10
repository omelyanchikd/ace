from firm import Firm
from worker import Worker


class World:
    def __init__(self, firm_count, workers_count):
        self.firms = []
        self.workers = []
        for i in range(firm_count):
            firm = Firm(i)
            self.firms.append(firm)

        for i in range(workers_count):
            worker = Worker(i)
            self.workers.append(worker)
            j = i % firm_count
            self.firms[j].add_worker(worker)

        for i in range(workers_count, workers_count + workers_count // 3):
            worker = Worker(i)
            self.workers.append(worker)

    def go(self):
        print("It's alive!!")
        for firm in self.firms:
            firm.work()
        for worker in self.workers:
            worker.work()
