import random
import math

import numpy

from .firm import Firm
#from firm_result import FirmResult
from .firm_labormarket_result import FirmLaborMarketResult
from .firm_goodmarket_result import FirmGoodMarketResult
from .worker import Worker
from .world import World


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

    def manage_job_offers(self):
        firms = self.firms
        salaries = []
        for firm_action in self.firm_labormarket_actions:
            if firm_action.salary >= 0 and firm_action.offer_count > 0:
                salaries.append(firm_action.salary)
            else:
                salaries.append(0)
        salaries = numpy.array(list(salaries))
        max_salary = max(salaries)
        quited = [[] for i in range(len(self.firms))]
        new_workers = [[] for i in range(len(self.firms))]

        potential_candidates = []
        for worker in self.households:
            if worker.employer is None or worker.salary < max_salary:
                potential_candidates.append(worker)

        while len(potential_candidates) > 0 and sum(salaries) > 0:
            worker = random.choice(potential_candidates)
            employer = numpy.random.choice(firms, replace=False, p=salaries / sum(salaries))
            assert isinstance(employer, Firm)

            potential_candidates.remove(worker)
            if worker.salary < salaries[employer.id]:
                new_workers[employer.id].append(worker)
                if worker.employer is not None:
                    quited[worker.employer].append(worker)
            if self.firm_labormarket_actions[employer.id].offer_count == len(new_workers[employer.id]):
                salaries[employer.id] = 0

        for firm in firms:
            self.firm_labormarket_results[firm.id] = FirmLaborMarketResult(new_workers[firm.id], quited[firm.id], firms[firm.id].salary)



    def manage_sales(self, firm_type):
        # Basic selection algorithm for good market
        if firm_type == 'RawFirm':
            self.manage_b2b_sales_raw()
        elif firm_type == 'CapitalFirm':
            self.manage_b2b_sales_capital()
        else:
            self.manage_b2c_sales()


    def manage_b2c_sales(self):
        if hasattr(self.households[0], 'consumption_budget') or hasattr(self.households[0], 'consumption_need'):
            self.manage_b2c_sales_active()
        else:
            self.manage_b2c_sales_passive()


    def manage_b2c_sales_passive(self):
        firms = self.production_firms
        sellers = self.production_firms
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        if hasattr(self, 'outside_world'):
            prices.append(self.outside_world.production_price)
            sellers.append(self.outside_world)
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
            seller = numpy.random.choice(sellers, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))

            if seller.id == 'OutsideWorld':
                if money >= self.outside_world.production_price:
                    self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': 'World',
                                                         'quantity': 1, 'money': self.outside_world.production_price})
                    self.outside_world.production_sales += self.outside_world.production_price
                    self.outside_world.production_sold += 1
            else:
                if money >= prices[seller.id]:
                    self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': 'World',
                                                         'quantity': 1, 'money': prices[seller.id].item()})
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


    def manage_b2c_sales_active(self):
        # Basic selection algorithm for good market
        if hasattr(self, 'outside_world'):
            if hasattr(self, 'government'):
                if hasattr(self.government, 'import_tax'):
                    import_production_price = self.outside_world.production_price * self.government.import_tax
                else:
                    import_production_price = self.outside_world.production_price
            else:
                import_production_price = self.outside_world.production_price
        sellers = self.production_firms
        firms = self.production_firms
        buyers = self.households
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        if hasattr(self, 'outside_world'):
            prices.append(import_production_price)
            sellers.append(self.outside_world)
            buyers.append(self.outside_world)
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
        while sum(selected_inverted_prices) > 0 and len(buyers) > 1:
            if hasattr(buyers[0], 'consumption_need'):
                if sum([buyer.consumption_need - buyer.consumption for buyer in buyers]) <= 0:
                    break
            if hasattr(buyers[0], 'consumption_budget'):
                if sum([buyer.consumption_budget for buyer in buyers]) <= min([price for price in prices if price > 0]):
                    break
            seller = numpy.random.choice(sellers, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            buyer = random.choice(buyers)

            if buyer.id != 'OutsideWorld':
                need = buyer.consumption_need - buyer.consumption if hasattr(buyer, 'consumption_need') else max(production_counts)
                budget = buyer.consumption_budget if hasattr(buyer, 'consumption_budget') else buyer.money

            if seller.id == 'OutsideWorld' and buyer.id == 'OutsideWorld':
                next
            if seller.id == 'OutsideWorld':
                bought = min(need, budget/self.outside_world.production_price)
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': import_production_price * bought})
                total_sold += bought
                self.outside_world.production_sold += bought
                self.outside_world.production_sales += bought * self.outside_world.production_price
                buyer.consumption += bought
                buyer.consumption_expenses += bought * import_production_price
                if hasattr(buyer, 'consumption_budget'):
                    buyer.consumption_budget -= bought * import_production_price
                if hasattr(self, 'government'):
                    if hasattr(self.government, 'import_tax'):
                        self.government.get_import_tax(self.step, bought * import_production_price)
            elif buyer.id == 'OutsideWorld':
                bought = min(1, production_counts[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                self.outside_world.production_bought += bought
                self.outside_world.production_expenses += bought * prices[seller.id]
                sales[seller.id] += bought
                production_counts[seller.id] -= bought
            else:
                bought = min(need, production_counts[seller.id], budget/prices[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                buyer.consumption += bought
                buyer.consumption_expenses += bought * prices[seller.id]
                sales[seller.id] += bought
                production_counts[seller.id] -= bought
                if hasattr(buyer, 'consumption_budget'):
                    buyer.consumption_budget -= bought * prices[seller.id]
                if production_counts[seller.id] <= 0:
                    prices[seller.id] = 0
                    inverted_prices[seller.id] = 0
                    selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
            if hasattr(buyer, 'consumption_need'):
                if buyer.consumption_need - buyer.consumption <= 0:
                    buyers.remove(buyer)
            if hasattr(buyer, 'constumption_budget'):
                if buyer.consumption_budget <= 0:
                    buyers.remove(buyer)


        #if total_sold < 2000:
           # sales = [0] * len(sales)
            #for firm in self.firms:
            #    firm.stock = 0
        for firm in firms:
            self.firm_goodmarket_results[firm.id] = FirmGoodMarketResult(sales[firm.id])
        #self.money = 1.5 * total_sold * 20 if total_sold > 0 else 1000


    def manage_b2b_sales_raw(self):
        # Basic selection algorithm for good market
        if hasattr(self, 'outside_world'):
            if hasattr(self, 'government'):
                if hasattr(self.government, 'import_tax'):
                    import_raw_price = self.outside_world.raw_price * self.government.import_tax
                else:
                    import_raw_price = self.outside_world.raw_price
            else:
                import_raw_price = self.outside_world.raw_price
        sellers = self.raw_firms
        firms = self.raw_firms
        buyers = [firm for firm in self.capital_firms or self.production_firms if hasattr(firm, 'raw_need')]
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        if hasattr(self, 'outside_world'):
            prices.append(import_raw_price)
            sellers.append(self.outside_world)
            buyers.append(self.outside_world)
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
        while sum(selected_inverted_prices) > 0 and len(buyers) > 1 and sum([firm.raw_need - firm.raw for firm in buyers if firm.id != 'OutsideWorld']) > 0 and min([price for price in prices if price != 0]) <= max([firm.raw_budget for firm in buyers if firm.id != 'OutsideWorld']):
            seller = numpy.random.choice(sellers, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            buyer = random.choice(buyers)

            if seller.id == 'OutsideWorld' and buyer.id == 'OutsideWorld':
                next
            if seller.id == 'OutsideWorld':
                bought = min(buyer.raw_need - buyer.raw, buyer.raw_budget/import_raw_price)
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': self.import_raw_price * bought})
                total_sold += bought
                self.outside_world.raw_sold += bought
                self.outside_world.raw_sales += bought * self.outside_world.raw_price
                buyer.raw_budget -= bought * import_raw_price
                buyer.raw += bought
                buyer.raw_expenses += bought * import_raw_price
                if hasattr(self, 'government'):
                    if hasattr(self.government, 'import_tax'):
                        self.government.get_import_tax(self.step, bought * import_raw_price)
            elif buyer.id == 'OutsideWorld':
                bought = min(1, production_counts[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                self.outside_world.raw_bought += bought
                self.outside_world.raw_expenses += bought * prices[seller.id]
                sales[seller.id] += bought
                production_counts[seller.id] -= bought
            else:
                bought = min(buyer.raw_need - buyer.raw, production_counts[seller.id], buyer.raw_budget/prices[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                buyer.raw_budget -= bought * prices[seller.id]
                buyer.raw += bought
                buyer.raw_expenses += bought * prices[seller.id]
                sales[seller.id] += bought
                production_counts[seller.id] -= bought
                if production_counts[seller.id] <= 0:
                    prices[seller.id] = 0
                    inverted_prices[seller.id] = 0
                    selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
            if buyer.raw_need - buyer.capital <= 0 or buyer.raw_budget <= 0:
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
        if hasattr(self, 'outside_world'):
            if hasattr(self, 'government'):
                if hasattr(self.government, 'import_tax'):
                    import_capital_price = self.outside_world.capital_price * self.government.import_tax
                else:
                    import_capital_price = self.outside_world.capital_price
            else:
                import_capital_price = self.outside_world.capital_price
        sellers = self.capital_firms
        firms = self.capital_firms
        buyers = [firm for firm in self.production_firms if hasattr(firm, 'capital_need')]
        prices = []
        for firm_action in self.firm_goodmarket_actions:
            if firm_action == 0:
                prices.append(0)
            elif firm_action.price >= 0 and firm_action.production_count > 0:
                prices.append(firm_action.price)
            else:
                prices.append(0)
        prices = numpy.array(list(prices))
        if hasattr(self, 'outside_world'):
            prices.append(import_capital_price)
            sellers.append(self.outside_world)
            buyers.append(self.outside_world)
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
        while sum(selected_inverted_prices) > 0 and len(buyers) > 1 and sum([firm.capital_need - firm.capital for firm in buyers if firm.id != 'OutsideWorld']) > 0 and min([price for price in prices if price != 0]) <= max([firm.capital_budget for firm in buyers if firm.id != 'OutsideWorld']):
            seller = numpy.random.choice(sellers, replace=False, p=selected_inverted_prices / sum(selected_inverted_prices))
            buyer = random.choice(buyers)
            if buyer.id == 'OutsideWorld' and seller.id == 'OutsideWorld':
                next
            
            if seller.id == 'OutsideWorld':
                bought = min(buyer.capital_need - buyer.capital, buyer.capital_budget/import_capital_price)
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': import_capital_price * bought})
                total_sold += bought
                self.outside_world.capital_sold += bought
                self.outside_world.capital_sales += bought * self.outside_world.capital_price
                buyer.capital_budget -= bought * import_capital_price
                buyer.capital += bought
                buyer.capital_expenses += bought * import_capital_price
                if hasattr(self, 'government'):
                    if hasattr(self.government, 'import_tax'):
                        self.government.get_import_tax(self.step, bought * import_capital_price)
            elif buyer.id == 'OutsideWorld':
                bought = min(1, production_counts[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                self.outside_world.capital_bought += bought
                self.outside_world.capital_expenses += bought * prices[seller.id]
                sales[seller.id] += bought
                production_counts[seller.id] -= bought
            else:
                bought = min(buyer.capital_need - buyer.capital, production_counts[seller.id], buyer.capital_budget/prices[seller.id])
                self.good_market_history.add_record({'step': self.step, 'seller_id': seller.id, 'buyer_id': buyer.id,
                                                     'quantity': bought, 'money': prices[seller.id] * bought})
                total_sold += bought
                sales[seller.id] += bought
                buyer.capital_budget -= bought * prices[seller.id]
                buyer.capital += bought
                buyer.capital_expenses += bought * prices[seller.id]
                production_counts[seller.id] -= bought
                if production_counts[seller.id] <= 0:
                    prices[seller.id] = 0
                    inverted_prices[seller.id] = 0
                    selected_inverted_prices = inverted_prices[[firm.id for firm in firms]]
            if buyer.capital_need - buyer.capital <= 0 or buyer.capital_budget <= 0:
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
