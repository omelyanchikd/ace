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

        self.price = 0
        self.salary = 0
        self.sold = 0
        self.stock = 0
        self.sales = 0
        self.salary = 0
        self.unemployment_rate = 0

        self.money = config['global']['initial_money']
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

    def manage_firm_actions(self, firm_actions):
        pass

    def compute_stats(self):
        self.price = 0
        self.stock = 0
        self.sales = 0
        self.sold = 0
        employed = 0
        for firm in self.firms:
            self.price += firm.price
            self.stock += firm.stock  # this needs to be rewritten, since in the end of iteration firm stock should be zero
            self.sold += firm.sold  # this needs to be rewritten, since sold is not firms parameter yet
            self.sales += firm.sales
            employed += len(firm.workers)
        if self.sold > 0:
            self.price /= self.sold
        else:
            self.price = 0
        if employed > 0:
            self.salary /= employed
        else:
            self.salary = 0
        unemployed = 0
        for worker in self.workers:
            if worker.employer is None:
                unemployed += 1
        if len(self.workers) > 0:
            self.unemployment_rate = unemployed / len(self.workers)


    def go(self):
        histories = []
        for i in range(len(self.firms)):
            histories.append(History(self.steps, self.firms[i].__class__.__name__))
        print("It's alive!!")
        birth_rate = self.config['global']['birth_rate']
        money_growth = self.config['global']['money_growth']
        for step in range(self.steps):
            # print("Step:", step)
            self.compute_stats()
            for firm in self.firms:
                # print(firm)
                firm.work()
                # print(firm)
                self.firm_actions[firm.id] = firm.decide()
            for j in range(birth_rate):
                worker = Worker(len(self.workers))
                self.workers.append(worker)
            self.manage_firm_actions(self.firm_actions)
            for firm_id, firm_action in enumerate(self.firm_actions):
                firm = self.firms[firm_id]
                firm.apply_result(self.firm_results[firm_id])
                histories[firm_id].add_record(step, firm)
            self.money += money_growth
        return histories
