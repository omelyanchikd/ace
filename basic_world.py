import random

import numpy

from firm import Firm
from firm_result import FirmResult
from worker import Worker
from world import World


def invert(x):
    if x != 0:
        return 1 / x
    else:
        return 0


class BasicWorld(World):
    def manage_firm_actions(self, firm_actions):
        """
        Basic World! Contains basic algorithms for labor market and good market.
        :param firm_actions:
        :return:
        """
        salaries = numpy.array(list(firm_action.salary if firm_action.salary >= 0 else 0 for firm_action in self.firm_actions))

        self.fire()

        new_workers, quited = self.manage_job_offers()

        sales = self.manage_sales()
        # Aggregate firm results
        for firm in self.firms:
            self.firm_results[firm.id] = FirmResult(new_workers[firm.id], quited[firm.id], salaries[firm.id],
                                                    sales[firm.id])

    def manage_job_offers(self):
        salaries = numpy.array(list(firm_action.salary for firm_action in self.firm_actions))
        max_salary = max(salaries)

        quited = [[] for i in range(len(self.firms))]
        new_workers = [[] for i in range(len(self.firms))]

        potential_candidates = []
        for worker in self.workers:
            if worker.employer is None or worker.salary < max_salary:
                potential_candidates.append(worker)

        while len(potential_candidates) > 0 and sum(salaries) > 0:
            worker = random.choice(potential_candidates)
            employer = numpy.random.choice(self.firms, replace=False, p=salaries / sum(salaries))
            assert isinstance(employer, Firm)

            potential_candidates.remove(worker)
            if worker.salary < salaries[employer.id]:
                new_workers[employer.id].append(worker)
                if worker.employer is not None:
                    quited[worker.employer].append(worker)
            if self.firm_actions[employer.id].offer_count == len(new_workers[employer.id]):
                salaries[employer.id] = 0

        return new_workers, quited

    def manage_sales(self):
        # Basic selection algorithm for good market
        prices = numpy.array(list(firm_action.price if firm_action.price >= 0 else 0 for firm_action in self.firm_actions))
        inverted_prices = numpy.array(list(invert(x) for x in prices))
        sales = [0] * len(self.firms)
        money = self.money
        for firm in self.firms:
            if self.firm_actions[firm.id].production_count > self.firms[firm.id].stock:
                self.firm_actions[firm.id].production_count = self.firms[firm.id].stock
        production_counts = numpy.array(list(firm_action.production_count for firm_action in self.firm_actions))
        while sum(prices) > 0 and money > 0:
            seller = numpy.random.choice(self.firms, replace=False, p=inverted_prices / sum(inverted_prices))
            assert isinstance(seller, Firm)

            sales[seller.id] += 1
            production_counts[seller.id] -= 1
            money -= prices[seller.id]
            if production_counts[seller.id] <= 0:
                prices[seller.id] = 0
                inverted_prices[seller.id] = 0
        return sales

    def fire(self):
        fired_workers = list(firm_action.fire_people for firm_action in self.firm_actions)

# for worker in fired_workers:
#            assert isinstance(worker, Worker)
#            worker.employer = None
#            worker.salary = 0
