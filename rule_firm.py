from firm import Firm
from firm_action import FirmAction

import random
import math

def isinrange(value, left, right):
    return left <= value < right

class RuleFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.plan = 50 * self.efficiency_coefficient

        self.salary_change = 0
        self.price_change = 0
        self.sold_change = 0
        self.workers_change = 0
        self.plan_change = 0

        self.prev_salary = self.salary
        self.prev_price = self.price
        self.prev_sold = self.sold
        self.prev_plan = self.plan
        self.prev_workers = len(self.workers)

        self.offer_count = 0

    def decide(self, stats):
        self.sold_change = (self.sold - self.prev_sold)/ self.prev_sold if self.prev_sold > 0 else 0
        self.workers_change = (len(self.workers) - self.prev_workers) / self.prev_workers if self.prev_workers > 0 else 0
        self.prev_salary = self.salary
        self.prev_price = self.price
        self.prev_plan = self.plan
        self.prev_sold = self.sold
        self.prev_workers = len(self.workers)
        if isinrange(self.sold_change, 0, 1) and isinrange(self.workers_change, 0, 1):
            self.salary_change = random.uniform(0, 1)
            self.price_change = random.uniform(0, 1)
            self.plan_change = random.uniform(0, 1)
        else:
            self.salary_change = 0
            self.price_change = 0
            self.plan_change = 0
        self.salary *= (1 + self.salary_change)
        self.price *= (1 + self.price_change)
        self.plan *= (1 + self.plan_change)
        self.salary_change = (self.salary - self.prev_salary)/ self.prev_salary if self.prev_salary > 0 else 0
        self.price_change = (self.price - self.prev_price) / self.prev_price if self.prev_price > 0 else 0
        self.plan_change = (self.plan - self.prev_plan) / self.prev_plan if self.prev_plan > 0 else 0

        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers) if math.floor(self.plan / self.efficiency_coefficient) - len(self.workers) > 0 else 0
        return FirmAction(self.offer_count, self.salary, self.stock, self.price, 0, 0, [])

