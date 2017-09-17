import random
import math

import numpy

from firm import Firm
#from firm_result import FirmResult
from firm_labormarket_result import FirmLaborMarketResult
from firm_goodmarket_result import FirmGoodMarketResult
from worker import Worker
from world import World


def invert(x):
    if x != 0:
        return 1 / x
    else:
        return 0


class BasicWorld(World):
    def manage_firm_actions(self, firm_actions, firm_type):
        """
        Basic World! Contains basic algorithms for labor market and good market.
        :param firm_actions:
        :return:
        """
        salaries = numpy.array(list(firm_action.salary if firm_action.salary >= 0 else 0 for firm_action in self.firm_actions))

        self.fire()

        new_workers, quited = self.manage_job_offers(firm_type)

        sales = self.manage_sales(firm_type)
        # Aggregate firm results
        #  for firm in self.firms:
        #     self.firm_results[firm.id] = FirmResult(new_workers[firm.id], quited[firm.id], salaries[firm.id],
        #                                            sales[firm.id])

    def manage_job_offers(self, firm_type = None):
        if firm_type == 'RawFirm':
            firms = self.raw_firms
        elif firm_type == 'CapitalFirm':
            firms = self.capital_firms
        elif firm_type == 'ProductionFirm':
            firms = self.production_firms
        else:
            firms = self.firms
        salaries = []
        for firm_action in self.firm_labormarket_actions:
            if firm_action == 0:
                salaries.append(0)
            elif firm_action.salary >= 0 and firm_action.offer_count > 0:
                salaries.append(firm_action.salary)
            else:
                salaries.append(0)
        salaries = numpy.array(list(salaries))
        selected_salaries = salaries[[firm.id for firm in firms]]
        max_salary = max(salaries)
        quited = [[] for i in range(len(self.firms))]
        new_workers = [[] for i in range(len(self.firms))]

        potential_candidates = []
        for worker in self.households:
            if worker.employer is None or worker.salary < max_salary:
                potential_candidates.append(worker)

        while len(potential_candidates) > 0 and sum(salaries) > 0:
            worker = random.choice(potential_candidates)
            employer = numpy.random.choice(firms, replace=False, p=selected_salaries / sum(selected_salaries))
            assert isinstance(employer, Firm)

            potential_candidates.remove(worker)
            if worker.salary < salaries[employer.id]:
                new_workers[employer.id].append(worker)
                if worker.employer is not None:
                    quited[worker.employer].append(worker)
            if self.firm_labormarket_actions[employer.id].offer_count == len(new_workers[employer.id]):
                salaries[employer.id] = 0
                selected_salaries = salaries[[firm.id for firm in firms]]

        for firm in firms:
            self.firm_labormarket_results[firm.id] = FirmLaborMarketResult(new_workers[firm.id], quited[firm.id], salaries[firm.id])



    def manage_sales(self, firm_type):
        # Basic selection algorithm for good market
        if firm_type == 'RawFirm':
            self.manage_b2b_sales_raw()
        elif firm_type == 'CapitalFirm':
            self.manage_b2b_sales_capital()
        else:
            self.manage_b2c_sales()


    def manage_b2c_sales(self):
        firms = self.production_firms
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        inverted_prices = numpy.array(list(invert(x) for x in prices))
        selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
        sales = [0] * len(self.firms)
        total_sold = 0
        money = self.money
        for firm in firms:
            if self.firm_goodmarket_actions[firm.id].production_count > self.firms[firm.id].stock:
                self.firm_goodmarket_actions[firm.id].production_count = self.firms[firm.id].stock
        production_counts = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                production_counts.append(0)
            else:
                production_counts.append(firm_action.production_count)
        production_counts = numpy.array(list(production_counts))
        while sum(selected_inverted_prices) > 0 and money > 0 and money >= min([price for price in prices if price != 0]):
            seller = numpy.random.choice(firms, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            assert isinstance(seller, Firm)

            if money >= prices[seller.id]:
                sales[seller.id] += 1
                total_sold += 1
                production_counts[seller.id] -= 1
                money -= prices[seller.id]
                if production_counts[seller.id] <= 0:
                    prices[seller.id] = 0
                    inverted_prices[seller.id] = 0
                    selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]

        #if total_sold < 2000:
           # sales = [0] * len(sales)
            #for firm in self.firms:
            #    firm.stock = 0
        for firm in firms:
            self.firm_goodmarket_results[firm.id] = FirmGoodMarketResult(sales[firm.id])
        #self.money = 1.5 * total_sold * 20 if total_sold > 0 else 1000

    def manage_b2b_sales_raw(self):
        # Basic selection algorithm for good market
        firms = self.raw_firms
        buyers = [firm for firm in self.capital_firms or self.production_firms]
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        inverted_prices = numpy.array(list(invert(x) for x in prices))
        selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
        sales = [0] * len(self.firms)
        total_sold = 0
        for firm in firms:
            if self.firm_goodmarket_actions[firm.id].production_count > self.firms[firm.id].stock:
                self.firm_goodmarket_actions[firm.id].production_count = self.firms[firm.id].stock
        production_counts = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                production_counts.append(0)
            else:
                production_counts.append(firm_action.production_count)
        production_counts = numpy.array(list(production_counts))
        while sum(selected_inverted_prices) > 0 and len(buyers) > 0 and sum([firm.raw_need for firm in buyers]) > 0 and min([price for price in prices if price != 0]) <= max([firm.raw_budget for firm in buyers]):
            seller = numpy.random.choice(firms, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            buyer = random.choice(buyers)
            assert isinstance(seller, Firm)


            if buyer.raw_need <= production_counts[seller.id] and buyer.raw_budget >= prices[seller.id]:
                if buyer.raw_budget >= prices[seller.id] * buyer.raw_need:
                    buyer.raw_budget -= prices[seller.id] * buyer.raw_need
                    production_counts[seller.id] -= buyer.raw_need
                    total_sold += buyer.raw_need
                    buyer.raw_need = 0
                else:
                    sold = int(math.floor(buyer.raw_budget / prices[seller.id]))
                    buyer.raw_budget -= prices[seller.id] * sold
                    production_counts[seller.id] -= sold
                    total_sold += sold
                    buyer.raw_need -= sold
            else:
                if buyer.raw_budget >= prices[seller.id] * production_counts[seller.id]:
                    buyer.raw_budget -= prices[seller.id] * production_counts[seller.id]
                    total_sold += production_counts[seller.id]
                    buyer.raw_need -= production_counts[seller.id]
                    production_counts[seller.id] = 0
                else:
                    sold = int(math.floor(buyer.raw_budget / prices[seller.id]))
                    buyer.raw_budget -= prices[seller.id] * sold
                    production_counts[seller.id] -= sold
                    total_sold += sold
                    buyer.raw_need -= sold
            if production_counts[seller.id] <= 0:
                prices[seller.id] = 0
                inverted_prices[seller.id] = 0
                selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
            if buyer.raw_need <= 0 or buyer.raw_budget <= 0:
                buyers.remove(buyer)

        #if total_sold < 2000:
           # sales = [0] * len(sales)
            #for firm in self.firms:
            #    firm.stock = 0
        for firm in firms:
            self.firm_goodmarket_results[firm.id] = FirmGoodMarketResult(sales[firm.id])
        #self.money = 1.5 * total_sold * 20 if total_sold > 0 else 1000
            
    def manage_b2b_sales_capital(self):
        # Basic selection algorithm for good market
        firms = self.capital_firms
        buyers = self.production_firms
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        inverted_prices = numpy.array(list(invert(x) for x in prices))
        selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
        sales = [0] * len(self.firms)
        total_sold = 0
        for firm in firms:
            if self.firm_goodmarket_actions[firm.id].production_count > self.firms[firm.id].stock:
                self.firm_goodmarket_actions[firm.id].production_count = self.firms[firm.id].stock
        production_counts = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                production_counts.append(0)
            else:
                production_counts.append(firm_action.production_count)
        production_counts = numpy.array(list(production_counts))
        while sum(selected_inverted_prices) > 0 and len(buyers) > 0 and sum([firm.capital_need for firm in buyers]) > 0 and min([price for price in prices if price != 0]) <= max([firm.raw_budget for firm in buyers]):
            seller = numpy.random.choice(firms, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            buyer = random.choice(buyers)
            assert isinstance(seller, Firm)

            if buyer.capital_need <= production_counts[seller.id]:
                if buyer.capital_budget >= prices[seller.id] * buyer.capital_need:
                    buyer.capital_budget -= prices[seller.id] * buyer.capital_need
                    production_counts[seller.id] -= buyer.capital_need
                    total_sold += buyer.capital_need
                    buyer.capital_need = 0
                else:
                    sold = int(math.floor(buyer.capital_budget / prices[seller.id]))
                    buyer.capital_budget -= prices[seller.id] * sold
                    production_counts[seller.id] -= sold
                    total_sold += sold
                    buyer.capital_need -= sold
            else:
                if buyer.capital_budget >= prices[seller.id] * production_counts[seller.id]:
                    buyer.capital_budget -= prices[seller.id] * production_counts[seller.id]
                    total_sold += production_counts[seller.id]
                    buyer.capital_need -= production_counts[seller.id]
                    production_counts[seller.id] = 0
                else:
                    sold = int(math.floor(buyer.capital_budget / prices[seller.id]))
                    buyer.capital_budget -= prices[seller.id] * sold
                    production_counts[seller.id] -= sold
                    total_sold += sold
                    buyer.capital_need -= sold
            if production_counts[seller.id] <= 0:
                prices[seller.id] = 0
                inverted_prices[seller.id] = 0
                selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
            if buyer.capital_need <= 0 or buyer.capital_budget <= 0:
                buyers.remove(buyer)

        #if total_sold < 2000:
           # sales = [0] * len(sales)
            #for firm in self.firms:
            #    firm.stock = 0
        for firm in firms:
            self.firm_goodmarket_results[firm.id] = FirmGoodMarketResult(sales[firm.id])
        #self.money = 1.5 * total_sold * 20 if total_sold > 0 else 1000


    def fire(self):
        fired_workers = list(firm_action.fire_people for firm_action in self.firm_actions)

# for worker in fired_workers:
#            assert isinstance(worker, Worker)
#            worker.employer = None
#            worker.salary = 0
