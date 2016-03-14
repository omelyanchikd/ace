from abc import ABCMeta, abstractmethod

import algorithms
from history import History
from worker import Worker


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
        self.config = config
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
        histories = []
        for i in range(len(self.firms)):
            histories.append(History(self.steps))
        print("It's alive!!")
        birth_rate = self.config['global']['birth_rate']
        for step in range(self.steps):
            # print("Step:", step)
            for firm in self.firms:
                # print(firm)
                firm.work()
                # print(firm)
                self.firm_actions[firm.id] = firm.decide()
            for j in range(birth_rate):
                worker = Worker(len(self.workers))
                self.workers.append(worker)
            for firm_id, firm_action in enumerate(self.firm_actions):
                firm_result = self.apply_firm_action(firm_id)
                firm = self.firms[firm_id]
                firm.apply_result(firm_result)
                histories[firm_id].add_record(step, firm)
        return histories
