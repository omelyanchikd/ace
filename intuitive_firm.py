from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class IntuitiveFirm(DecisionMaker):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.prev_workers = 50
        self.offer_count = 0
        self.period = 3
        self.history = [1000, 1000, 1000]
        self.plan = 50 & self.efficiency_coefficient
        self.smoothing_coefficient = 0.5

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)


    def decide_salary(self, stats):
        if self.sold >= self.plan and self.sold > 0:
            self.plan = 1.1 *(self.smoothing_coefficient * self.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history))
        else:
            self.plan = self.smoothing_coefficient * self.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history)
        self.history.append(self.sold)
        self.history.pop(0)
        self.plan = self.plan // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan > 0 else self.efficiency_coefficient
        if len(self.workers) < self.prev_workers + self.offer_count:
            self.salary *= 1.01
        else:
            self.salary *= 0.99
        self.offer_count = self.plan // self.efficiency_coefficient - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.prev_workers = len(self.workers)
        total_salary = sum([worker.salary for worker in self.workers])
        self.price = 1.05 * (total_salary + self.salary)/self.plan
        self.price = self.price if self.price > 0 else 0
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])