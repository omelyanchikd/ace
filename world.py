from firm import Firm
from worker import Worker
import algorithms


class World:
    def __init__(self, workers_count):
        self.firms = []
        self.workers = []
        self.algorithms = {
            10: 'BaseAlgorithm'
        }
        firm_counter = 0
        for count, class_ in self.algorithms.items():
            for i in range(count):
                algo_class = getattr(algorithms, class_)
                firm = Firm(firm_counter, algo_class())
                self.firms.append(firm)
                firm_counter += 1
        self.results = [0] * firm_counter
        for i in range(workers_count):
            worker = Worker(i)
            self.workers.append(worker)
            j = i % firm_counter
            self.firms[j].add_worker(worker)

        for i in range(workers_count, workers_count + workers_count // 3):
            worker = Worker(i)
            self.workers.append(worker)

    def go(self):
        print("It's alive!!")
        for firm in self.firms:
            self.results[firm.id] = firm.work()
        for worker in self.workers:
            worker.work()
