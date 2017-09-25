from decision_maker import DecisionMaker
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


class NonconsciousFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.plan = firm.plan
        self.salary = firm.salary
        self.offer_count = 0
        self.probabilities = [1/9] * 9
        self.actions = [(0.01, firm.labor_productivity), (0.01, 0), (0.01, -firm.labor_productivity),
                        (0, firm.labor_productivity), (0, 0), (0, -firm.labor_productivity),
                        (-0.01, firm.labor_productivity), (-0.01, 0), (-0.01, -firm.labor_productivity)]
        self.action = (0,0)
        self.type = "NonconsciousFirm"

    def decide(self, stats, firm):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats, firm):
        self.probabilities = update(self.probabilities, firm.sold * firm.profit/firm.price, self.actions.index(self.action))
        distribution = numpy.array(self.probabilities)
        indexes = [i for i in range(0, len(self.probabilities))]
        self.action = self.actions[numpy.random.choice(indexes, replace = False, p = distribution/sum(distribution))]
        firm.price *= (1 + self.action[0])
        firm.price = firm.price if firm.price > 0 else 0
        firm.plan += self.action[1]
        firm.plan = (firm.plan - firm.stock) // firm.labor_productivity * firm.labor_productivity
        firm.plan = firm.plan if firm.plan >= 0 else 0
        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        total_salary = sum([worker.salary for worker in firm.workers])
        while True:
            if self.offer_count > 0:
                firm.salary = 0.95 * (
                    firm.price * (len(firm.workers) + self.offer_count) * firm.labor_productivity -
                    total_salary) / self.offer_count
                if firm.salary > 0:
                    break
                firm.price *= 1.05
            else:
                break
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
