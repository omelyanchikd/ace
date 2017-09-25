from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import random
import math

def isinrange(value, left, right):
    return left <= value < right

def change(new_value, old_value):
    return (new_value - old_value)/old_value if old_value > 0 else 0

class RuleFirm(DecisionMaker):
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

        self.rules_salary = [[0, 0.1, 0, 1, 0, 0.05],
                             [0.1, 0.3, 1, 3, 0, 0.05],
                             [-0.1, 0, 0, 1, -0.05, 0],
                             [-0.3, -0.1, 0, 1, -0.1, -0.05]]
        self.rules_plan = [[0, 0.1, 0, 1, 0, 0.1],
                           [0.1, 0.3, 1, 3, 0, 0.05],
                           [-0.1, 0, 0, 1, -0.1, 0],
                           [-0.3, -0.1, 0, 1, -0.3, -0.1]]

        self.offer_count = 0

        self.type = "RuleFirm"


    def decide_salary(self, stats, firm):
        self.profit_change = change(firm.profit, self.prev_profit)
        self.sales_change = change(firm.sales, self.prev_sales)
        self.sold_change = change(firm.sold, self.prev_sold)
        #self.workers_change = (len(self.workers) - self.prev_workers) / self.prev_workers if self.prev_workers > 0 else 0
        self.workers_change = len(firm.workers) - self.prev_workers

        #state = list(self.profit_change, self.sales_change, self.workers_change, self.sold_change)
        state = [self.sales_change, self.workers_change]
        firm.salary *= (1 + self.get_parameter(self.rules_salary, state))
        firm.salary = firm.salary if firm.salary > 0 else 0
        #self.price *= (1 + self.price_change)
        firm.price = 1.05 * firm.salary / firm.labor_productivity
        firm.plan = (1 + self.get_parameter(self.rules_plan, state)) * firm.plan - firm.stock
        firm.plan = firm.plan if firm.plan > 0 else 0
        self.salary_change = change(firm.salary, self.prev_salary)
        self.price_change = change(firm.price, self.prev_price)
        self.plan_change = change(firm.plan, self.prev_plan)

        self.prev_salary = firm.salary
        self.prev_price = firm.price
        self.prev_plan = firm.plan
        self.prev_sold = firm.sold
        self.prev_workers = len(firm.workers)
        self.prev_sales = firm.sales
        self.prev_profit = firm.profit

        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        firm.labor_capacity = len(firm.workers) + self.offer_count

        return FirmLaborMarketAction(self.offer_count, firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def get_parameter(self, rules, state):
        for rule in rules:
            for i in range(0, 2 * len(state), 2):
                if state[i//2] < rule[i] or state[i//2] >= rule[i+1]:
                    break
            if i == 2 * len(state):
                return random.uniform(rule[2 * len(state)], rule[2 * len(state) + 1])
        select = random.randint(0, len(rules) - 1)
        return random.uniform(rules[select][2 * len(state)], rules[select][2 * len(state) + 1])
