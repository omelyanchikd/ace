from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import math
import random


def change(new_value, old_value):
    return (new_value - old_value) / old_value if old_value > 0 else 0


def check_margin(salary, workers, expected):
    return 1 - salary * workers / expected > 0.05 if expected > 0 else 0


class MosesFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = firm.salary
        self.plan = firm.plan

        self.salary_change = 0
        self.price_change = 0
        self.sold_change = 0
        self.workers_change = 0
        self.plan_change = 0
        self.sales_change = 0
        self.profit_change = 0

        self.prev_salary = firm.salary
        self.prev_price = firm.price
        self.prev_sold = firm.sold
        self.prev_plan = firm.plan
        self.prev_workers = len(firm.workers)
        self.prev_sales = firm.sales
        self.prev_profit = firm.profit

        self.exp_sales = 0.1
        self.exp_sold = 0.1

        self.expected = 0
        self.type = "MosesFirm"

    def decide_salary(self, stats, firm):
        self.sales_change = change(firm.sales, self.prev_sales)
        self.sold_change = change(firm.sold, self.prev_sold)

        self.prev_sold = firm.sold
        self.prev_sales = firm.sales

        expected_sales_growth = 0.05 # Get correct value for expected_sales_growth from stats
        expected_sold_growth = 0.05  # Get correct value for expected_sold_growth from stats

        self.exp_sales = 0.5 * self.sales_change + 0.5 * expected_sales_growth
        self.exp_sold = 0.5 * self.sold_change + 0.5 * expected_sold_growth

        self.expected = (1 + self.exp_sales) * firm.sales
        self.plan = (1 + self.exp_sold) * firm.sold

        self.expected = self.expected if self.expected >= 0 else 0

        firm.plan = (firm.plan - firm.stock) // firm.labor_productivity * firm.labor_productivity
        firm.plan = firm.plan if firm.plan >= 0 else 0

        firm.price = self.expected / firm.plan if firm.plan > 0 and self.expected > 0 else firm.price
        firm.salary = 0.95 * firm.price * firm.labor_productivity

        while not (
        check_margin(firm.salary, firm.plan // firm.labor_productivity, self.expected)) and self.expected != 0:
            if firm.profit >= 0:
                firm.salary *= 0.95
            else:
                firm.plan = firm.plan // firm.labor_productivity - 1
                firm.price = self.expected / firm.plan if firm.plan > 0 and self.expected > 0 else firm.price
                firm.salary = 0.95 * firm.price * firm.labor_productivity
        firm.plan = firm.plan if firm.plan >= 0 else 0
        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        if firm.salary == 0:
            while (len(firm.workers) > 0):
                worker = list(firm.workers)[0]
                firm.fire_worker(worker)
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)