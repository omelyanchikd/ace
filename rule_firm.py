from firm import Firm
from firm_action import FirmAction

import random
import math

def isinrange(value, left, right):
    return left <= value < right

def change(new_value, old_value):
    return (new_value - old_value)/old_value if old_value > 0 else 0

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
        self.sales_change = 0
        self.profit_change = 0

        self.prev_salary = self.salary
        self.prev_price = self.price
        self.prev_sold = self.sold
        self.prev_plan = self.plan
        self.prev_workers = len(self.workers)
        self.prev_sales = self.sales
        self.prev_profit = self.profit

        self.offer_count = 0

    def decide(self, stats):
        self.profit_change = change(self.profit, self.prev_profit)
        self.sales_change = change(self.sales, self.prev_sales)
        self.sold_change = change(self.sold, self.prev_sold)
        #self.workers_change = (len(self.workers) - self.prev_workers) / self.prev_workers if self.prev_workers > 0 else 0
        self.workers_change = len(self.workers) - self.prev_workers
        self.prev_salary = self.salary
        self.prev_price = self.price
        self.prev_plan = self.plan
        self.prev_sold = self.sold
        self.prev_workers = len(self.workers)
        self.prev_sales = self.sales
        self.prev_profit = self.profit
        if isinrange(self.sold_change, -0.1, 0.1) and isinrange(self.workers_change, 0, 1):
            self.salary_change = random.uniform(0, 0.05)
            #self.price_change = random.uniform(0, 0.05)
            self.plan_change = random.uniform(0, 0.05)
        elif isinrange(self.sold_change, 0.1, 0.3) and isinrange(self.workers_change, 0, 1):
            self.salary_change = random.uniform(0.05, 0.1)
            #self.price_change = random.uniform(0.05, 0.1)
            self.plan_change = random.uniform(0.05, 0.1)
        elif isinrange(self.sold_change, 0.3, 0.5) and isinrange(self.workers_change, 1, 3):
            self.salary_change = random.uniform(0.1, 0.2)
            #self.price_change = random.uniform(0.1, 0.2)
            self.plan_change = random.uniform(0.1, 0.2)
        elif isinrange(self.sold_change, 0.5, math.inf) and isinrange(self.workers_change, 3, math.inf):
            self.salary_change = random.uniform(0.2, 0.3)
            #self.price_change = random.uniform(0.2, 0.3)
            self.plan_change = random.uniform(0.2, 0.3)
        elif isinrange(self.sold_change, -0.3, -0.1) and isinrange(self.workers_change, -1, 0):
            self.salary_change = random.uniform(-0.05, 0)
            #self.price_change = random.uniform(-0.05, 0)
            self.plan_change = random.uniform(-0.05, 0)
        elif isinrange(self.sold_change, -0.3, 0.5) and isinrange(self.workers_change, -3, -1):
            self.salary_change = random.uniform(-0.1, -0.2)
            #self.price_change = random.uniform(-0.1, -0.2)
            self.plan_change = random.uniform(-0.1, -0.2)
        elif isinrange(self.sold_change, -math.inf, -0.5) and isinrange(self.workers_change, -math.inf, -3):
            self.salary_change = random.uniform(-0.2, -0.3)
            #self.price_change = random.uniform(-0.2, -0.3)
            self.plan_change = random.uniform(-0.2, -0.3)
        else:
            self.salary_change = 0
            #self.price_change = 0
            self.plan_change = 0
        self.salary *= (1 + self.salary_change)
        self.salary = self.salary if self.salary > 0 else 0
        #self.price *= (1 + self.price_change)
        self.price = self.salary / (0.95 * self.efficiency_coefficient)
        self.plan *= (1 + self.plan_change)
        self.plan = self.plan if self.plan > 0 else 0
        self.salary_change = change(self.salary, self.prev_salary)
        self.price_change = change(self.price, self.prev_price)
        self.plan_change = change(self.plan, self.prev_plan)

        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        return FirmAction(self.offer_count, self.salary, self.stock, self.price, 0, 0, [])

