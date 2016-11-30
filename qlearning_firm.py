from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy

def argmax(two_dimensional_list, dimension):
    arg_max = 0
    max_val = two_dimensional_list[dimension][0]
    for i in range(0,len(two_dimensional_list[dimension])):
        if two_dimensional_list[dimension][i] > max_val:
            max_val = two_dimensional_list[dimension][i]
            arg_max = i
    return arg_max

class QlearningFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.plan = 50 * self.efficiency_coefficient
        self.salary = 200
        self.offer_count = 0
        self.prev_workers = 50
        self.actions = [(0.01, self.efficiency_coefficient), (0.01, 0), (0.01, -self.efficiency_coefficient),
                        (0, self.efficiency_coefficient), (0, 0), (0, -self.efficiency_coefficient),
                        (-0.01, self.efficiency_coefficient), (-0.01, 0), (-0.01, -self.efficiency_coefficient)]
        self.action = (0,0)
        self.state = 0
        self.alpha = 0.5
        self.gamma = 0.5
        self.q = []
        for state in range(0, 6):
            self.q.append([])
            for action in range(0, 9):
                self.q[state].append(100)

    def decide(self, stats):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats):
        self.update_state()
        self.prev_workers = len(self.workers)
        self.update()
        self.action = self.actions[argmax(self.q, self.state)]
        self.price *= (1 + self.action[0])
        self.price = self.price if self.price > 0 else 0
        self.plan += self.action[1]
        self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        total_salary = sum([worker.salary for worker in self.workers])
        while True:
            if self.offer_count > 0:
                self.salary = 0.95 * (
                self.price * (len(self.workers) + self.offer_count) * self.efficiency_coefficient -
                total_salary) / self.offer_count
                if self.salary > 0:
                    break
                self.price *= 1.05
            else:
                break
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def update_state(self):
        if len(self.workers) == 0:
            self.state = 5
        elif self.sold == 0:
            self.state = 4
        elif self.sold >= self.plan and len(self.workers) == self.prev_workers + self.offer_count:
            self.state = 0
        elif self.sold < self.plan and len(self.workers) == self.prev_workers + self.offer_count:
            self.state = 1
        elif self.sold == self.plan and len(self.workers) < self.prev_workers + self.offer_count:
            self.state = 2
        else:
            self.state = 3

    def update(self):
        current_action = self.actions.index(self.action)
        self.q[self.state][current_action] = self.q[self.state][current_action] + self.alpha * (self.profit + self.gamma * max(self.q[self.state]) - self.q[self.state][current_action])


