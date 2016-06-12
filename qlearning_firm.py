from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy


def update(probabilities, reward, action):
    new_probabilities = probabilities
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


class QlearningFirm(Firm):
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

    def decide(self, stats):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats):
        self.probabilities = update(self.probabilities, self.profit, self.actions.index(self.action))
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
        self.salary = 0.95 * self.price * self.efficiency_coefficient
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)
