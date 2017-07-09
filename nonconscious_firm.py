from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy


def transform(x):
    return 2/math.pi * math.atan(x/500000)

def update(probabilities, reward, action):
    new_probabilities = probabilities
    if reward != 0:
        print(transform(reward))
    if reward < 0:
        for i in range(0, len(probabilities)):
            if i == action:
                new_probabilities[i] = probabilities[i] - transform(-reward) * probabilities[i]
            else:
                new_probabilities[i] = probabilities[i] + transform(-reward) * probabilities[i] * probabilities[action] /(1 - probabilities[action])
    elif reward > 0:
        for i in range(0, len(probabilities)):
            if i == action:
                new_probabilities[i] = probabilities[i] + transform(reward) * (1 - probabilities[i])
            else:
                new_probabilities[i] = probabilities[i] - transform(reward) * probabilities[i]
    return new_probabilities


class NonconsciousFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.plan = 50 * self.efficiency_coefficient
        self.salary = 200
        self.offer_count = 0
        self.probabilities = [1/9] * 9
        self.actions = [(0.01, self.efficiency_coefficient), (0.01, 0), (0.01, -self.efficiency_coefficient),
                        (0, self.efficiency_coefficient), (0, 0), (0, -self.efficiency_coefficient),
                        (-0.01, self.efficiency_coefficient), (-0.01, 0), (-0.01, -self.efficiency_coefficient)]
        self.action = (0,0)
        self.type = "NonconsciousFirm"

    def decide(self, stats):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats):
        self.probabilities = update(self.probabilities, self.sold * self.profit/self.price, self.actions.index(self.action))
        distribution = numpy.array(self.probabilities)
        indexes = [i for i in range(0, len(self.probabilities))]
        self.action = self.actions[numpy.random.choice(indexes, replace = False, p = distribution/sum(distribution))]
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
