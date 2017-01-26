from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random


def change(new_value, old_value):
    return (new_value - old_value) / old_value if old_value > 0 else 0


def check_margin(salary, workers, expected):
    return 1 - salary * workers / expected > 0.05 if expected > 0 else 0


class MosesFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.plan = 50 * self.efficiency_coefficient

        self.salary_change = 0
        self.price_change = 0
        self.sold_change = 0
        self.workers_change = 0
        self.plan_change = 0
        self.sales_change = 0
        self.profit_change = 0

        self.prev_salary = self.salary
        self.prev_price = self.price
        self.prev_sold = self.sold
        self.prev_plan = self.plan
        self.prev_workers = len(self.workers)
        self.prev_sales = self.sales
        self.prev_profit = self.profit

        self.exp_sales = 0.1
        self.exp_sold = 0.1

        self.expected = 0

    def decide_salary(self, stats):
        self.sales_change = change(self.sales, self.prev_sales)
        self.sold_change = change(self.sold, self.prev_sold)

        self.prev_sold = self.sold
        self.prev_sales = self.sales

        self.exp_sales = 0.5 * self.sales_change + 0.5 * stats.expected_sales_growth
        self.exp_sold = 0.5 * self.sold_change + 0.5 * stats.expected_sold_growth

        self.expected = (1 + self.exp_sales) * self.sales
        self.plan = (1 + self.exp_sold) * self.sold

        self.expected = self.expected if self.expected >= 0 else 0

        self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0

        self.price = self.expected / self.plan if self.plan > 0 and self.expected > 0 else self.price
        self.salary = 0.95 * self.price * self.efficiency_coefficient

        while not (
        check_margin(self.salary, self.plan // self.efficiency_coefficient, self.expected)) and self.expected != 0:
            if self.profit >= 0:
                self.salary *= 0.95
            else:
                self.plan = self.plan // self.efficiency_coefficient - 1
                self.price = self.expected / self.plan if self.plan > 0 and self.expected > 0 else self.price
                self.salary = 0.95 * self.price * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        if self.salary == 0:
            for worker in self.workers:
                self.fire_worker(worker)
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)