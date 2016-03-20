import numpy
import random

from firm import Firm
from firm_action import FirmAction
from firm_result import FirmResult
from world import World


class BasicWorld(World):
    def manage_firm_actions(self, firm_actions):
        """
        Basic World! Contains basic algotithms for labor market and good market.
        :param firm_actions:
        :return:
        """
        prices = [0] * len(self.firms)
        salaries = [0] * len(self.firms)
        workers = [[] for i in range(len(self.firms))]
        sales = [0] * len(self.firms)

        for firm_id, firm_action in enumerate(self.firm_actions):
            # Read actions in
            firm_action = self.firm_actions[firm_id]
            assert isinstance(firm_action, FirmAction)

            # Fire fired workers
            fired_workers = firm_action.fire_people
            for id in fired_workers:
                self.workers[id].employer = None

            # Get new salary and price info
            prices[firm_id] = firm_action.price
            salaries[firm_id] = firm_action.salary

            # If the firm has nothing to sell or nobody to hire, price and salary should be equal to 0
            if firm_action.offer_count == 0:
                salaries[firm_id] = 0
            if firm_action.production_count == 0:
                prices[firm_id] = 0

        prices = numpy.array(prices)
        salaries = numpy.array(salaries)
        # Basic selection algorithm for labor market
        unemployed_workers = []
        for worker in self.workers:
            if worker.employer is None:
                unemployed_workers.append(worker)
        while len(unemployed_workers) > 0 and sum(salaries) > 0:
            worker = random.choice(unemployed_workers)
            employer = numpy.random.choice(self.firms, replace=False, p=salaries / sum(salaries))
            assert isinstance(employer, Firm)
            unemployed_workers.remove(worker)
            # this shoud be rewritten, but I don't know how yet
            workers[employer.id].append(worker)
            if self.firm_actions[employer.id].offer_count == len(workers[employer.id]):
                salaries[employer.id] = 0

        # Basic selection algorithm for good market
        while sum(prices) > 0 and self.money > 0:
            seller = numpy.random.choice(self.firms, replace=False, p=prices / sum(prices))
            assert isinstance(seller, Firm)

            sales[seller.id] += 1
            self.money -= prices[seller.id]
            if self.firm_actions[seller.id].production_count == sales[seller.id]:
                prices[seller.id] = 0

        # Aggregate firm results
        for firm in self.firms:
            self.firm_results[firm.id] = FirmResult(workers[firm.id], salaries[firm.id], sales[firm.id])



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
