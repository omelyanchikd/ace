import numpy
import random

from firm import Firm
from firm_action import FirmAction
from firm_result import FirmResult
from world import World


class BasiclWorld(World):
    def manage_firm_actions(self, firm_actions):
        """
        Basic World! Contains basic algotithms for labor market and good market.
        :param firm_actions:
        :return:
        """
        prices = [0] * len(self.firms)
        salaries = [0] * len(self.firms)
        workers = [0] * len(self.firms)

        for firm_id, firm_action in enumerate(self.firm_actions):
            firm_action = self.firm_actions[firm_id]
            assert isinstance(firm_action, FirmAction)

            prices[firm_id] = firm_action.price

            if firm_action.offer_count > 0:
                salaries[firm_id] = firm_action.salary

        # Basic selection algorithm for labor market
        unemployed_workers = []
        for worker in self.workers:
            if worker.employer is None:
                unemployed_workers.append(worker)
        while len(unemployed_workers) > 0:
            worker = random.choice(unemployed_workers)
            employer = numpy.random.choice(self.firms, p=salaries / sum(salaries))
            unemployed_workers.remove(worker)
            assert isinstance(employer, Firm)
            # this shoud be rewritten, but I don't know how yet
            (workers[employer.id]).append(worker)
            if self.firm_actions[employer.id].offer_count == len(workers[employer.id]):
                salaries[employer.id] = 0

                #Basic selection algorithm for good market


    def apply_firm_action(self, firm_id):
        """
        Basic World! Contains basic algorithms for labor market and good market.

        :type firm_id: int
        """
        firm_action = self.firm_actions[firm_id]
        assert isinstance(firm_action, FirmAction)

        workers_count = firm_action.offer_count
        workers = []
        # here you have everyone non-employed
        for worker in self.workers:
            if worker.employer is None:
                workers.append(worker)
                workers_count -= 1
                if workers_count == 0:
                    break
        # if it's not enough - here you have more!
        # if workers_count > 0:
        #    for w in range(workers_count):
        #        new_worker_id = len(self.workers)
        #        worker = Worker(new_worker_id)
        #        self.workers.append(worker)
        #        workers.append(worker)
        # all your stuff is sold!
        sold_count = firm_action.production_count
        return FirmResult(workers, firm_action.salary, sold_count)
