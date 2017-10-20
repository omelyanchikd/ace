from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import math
import random

def expected_profit_margin(firm, expected):
    raw_budget = firm.raw_budget if hasattr(firm, 'raw_budget') else 0
    capital_budget = firm.capital_budget if hasattr(firm, 'capital_budget') else 0
    capital_amortization = firm.capital_amortization if hasattr(firm, 'capital_amortization') else 0

    return (expected - firm.salary_budget - raw_budget - capital_amortization * capital_budget)/expected

def change(new_value, old_value):
    if isinstance(new_value, set):
        return (len(new_value) - len(old_value))/len(old_value) if len(old_value) != 0 else 0
    return (new_value - old_value)/old_value if old_value != 0 else 0


def check_margin(firm, control_parameters, derived_parameters, expected):
    for parameter in derived_parameters:
        setattr(firm, parameter, firm.derive(parameter, control_parameters))
    return expected_profit_margin(firm, expected) > 0.05 if expected > 0 else 0


class MosesFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)

        self.sold_change = 0
        self.sales_change = 0
        self.raw_price_change = 0
        self.stats_raw_price_change = 0
        self.capital_price_change = 0
        self.stats_capital_price_change = 0

        self.prev_sold = firm.sold
        self.prev_sales = firm.sales
        self.prev_raw_price = 0
        self.prev_capital_price = 0
        self.stats_raw_price_change = 0
        self.stats_capital_price_change = 0

        self.exp_sales = 0.1
        self.exp_sold = 0.1
        self.exp_raw_price = 0.1
        self.exp_capital_price = 0.1

        self.expected = 0
        self.type = "MosesFirm"

    def decide_salary(self, stats, firm):
        control_parameters = ['plan', 'price', 'salary']
        derived_parameters = ['labor_capacity', 'salary_budget']

        self.sales_change = change(firm.sales, self.prev_sales)
        self.sold_change = change(firm.sold, self.prev_sold)

        self.prev_sold = firm.sold
        self.prev_sales = firm.sales

        self.exp_sales = 0.5 * self.sales_change + 0.5 * stats.expected_sales_growth
        self.exp_sold = 0.5 * self.sold_change + 0.5 * stats.expected_sold_growth

        self.expected = (1 + self.exp_sales) * firm.sales
        self.expected = self.expected if self.expected >= 0 else 0

        firm.plan = (1 + self.exp_sold) * firm.sold
        firm.price = self.expected / firm.plan if firm.plan > 0 and self.expected > 0 else firm.price

        if hasattr(firm, 'raw'):
            self.raw_price_change = change(firm.raw_budget/firm.raw, self.prev_raw_price)
            self.stats_raw_price_change = change(stats.raw_price, self.stats_raw_price_change)
            self.exp_raw_price = 0.5 * self.raw_price_change + 0.5 * self.stats_raw_price_change
            self.prev_raw_price = firm.raw_budget/firm.raw
            self.prev_stats_raw_price = stats.raw_price

            firm.raw_budget = firm.plan / firm.raw_productivity * (1 + self.exp_raw_price) * stats.raw_price
            control_parameters.append('raw_budget')
            derived_parameters.append('raw_need')

        if hasattr(firm, 'capital'):
            self.capital_price_change = change(firm.capital_budget / firm.capital, self.prev_capital_price)
            self.stats_capital_price_change = change(stats.capital_price, self.stats_capital_price_change)
            self.exp_capital_price = 0.5 * self.capital_price_change + 0.5 * self.stats_capital_price_change
            self.prev_capital_price = firm.capital_budget/firm.capital
            self.prev_stats_capital_price = stats.capital_price

            firm.capital_budget = (firm.plan / firm.capital_productivity - firm.capital) * stats.capital_price * (1 + self.capital_raw_price)
            control_parameters.append('capital_budget')
            derived_parameters.append('capital_need')

        firm.salary = firm.derive_salary(control_parameters)

        tries = 0

        while not (check_margin(firm, control_parameters, derived_parameters, self.expected)) and self.expected != 0 and tries < 100:
            if firm.profit >= 0:
                firm.salary *= 0.95
            else:
                firm.plan = math.floor(firm.plan / firm.labor_productivity) - 1
                firm.price = self.expected / firm.plan if firm.plan > 0 and self.expected > 0 else firm.price
                if hasattr(firm, 'raw'):
                    firm.raw_budget = firm.plan / firm.raw_productivity * self.exp_raw_price

                if hasattr(firm, 'capital'):
                    firm.capital_budget = (firm.plan / firm.capital_productivity - firm.capital) * self.capital_raw_price

                firm.salary = firm.derive_salary(control_parameters)
            tries += 1


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)