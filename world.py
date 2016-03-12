from firm import Firm
from worker import Worker
import algorithms


class World:
    def __init__(self, config):
        self.firms = []
        self.workers = []
        self.steps = config['global']['steps']
        algorithm_class = config['global']['world_algorithm']
        self.world_algorithm = getattr(algorithms, algorithm_class)

        self.firm_algorithms = config['algorithms']
        workers_count = config['global']['workers_count']
        firm_count = 0
        for class_, count in self.firm_algorithms.items():
            for i in range(int(count)):
                algorithm_class = getattr(algorithms, class_)
                firm = Firm(firm_count, algorithm_class())
                self.firms.append(firm)
                firm_count += 1
        # initial worker distribution
        for i in range(workers_count):
            worker = Worker(i)
            self.workers.append(worker)
            firm_id = i % firm_count
            self.firms[firm_id].add_worker(worker)

        self.firm_actions = [0] * firm_count
        self.firm_results = [0] * firm_count

    def apply_firm_action(self, firm_id):
        return self.world_algorithm.apply(self.world_algorithm, self, firm_id)

    def go(self):
        print("It's alive!!")
        for i in range(self.steps):
            for firm in self.firms:
                self.firm_actions[firm.id] = firm.work()
            for firm_id, firm_action in enumerate(self.firm_actions):
                firm_result = self.apply_firm_action(firm_id)
                self.firms[firm_id].apply_result(firm_result)
