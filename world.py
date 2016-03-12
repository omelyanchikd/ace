from firm import Firm
from worker import Worker
import algorithms
from abc import ABCMeta, abstractmethod


class World:
    __metaclass__ = ABCMeta

    @abstractmethod
    def apply_firm_action(self, firm_id):
        pass

    def __init__(self, config):
        self.firms = []
        self.workers = []
        self.steps = config['global']['steps']

        self.firm_algorithms = config['algorithms']
        workers_count = config['global']['workers_count']
        firm_counter = 0
        for class_, count in self.firm_algorithms.items():
            for i in range(int(count)):
                firm_class = getattr(algorithms, class_)
                firm = firm_class(firm_counter)
                self.firms.append(firm)
                firm_counter += 1
        firm_count = firm_counter
        # initial worker distribution
        for i in range(workers_count):
            worker = Worker(i)
            self.workers.append(worker)
            firm_id = i % firm_count
            firm = self.firms[firm_id]
            firm.add_worker(worker, firm.current_salary)

        self.firm_actions = [0] * firm_count
        self.firm_results = [0] * firm_count

    def go(self):
        print("It's alive!!")
        for i in range(self.steps):
            print("Step:", i)
            for firm in self.firms:
                print(firm)
                firm.work()
                self.firm_actions[firm.id] = firm.decide()
            for firm_id, firm_action in enumerate(self.firm_actions):
                firm_result = self.apply_firm_action(firm_id)
                self.firms[firm_id].apply_result(firm_result)
