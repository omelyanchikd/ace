from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class IntuitiveFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.prev_workers = 0
        self.offer_count = 0
        self.period = 3
        self.history = [1000, 1000, 1000]
        self.plan = 50 & self.efficiency_coefficient
        self.smoothing_coefficient = 0.5

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)


    def decide_salary(self, stats):
        if self.sold >= self.plan:
            self.plan = 1.1 *(self.smoothing_coefficient * self.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history))
        else:
            self.plan = self.smoothing_coefficient * self.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history)
        self.history.append(self.sold)
        self.history = self.history[1:len(self.history)]
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        if len(self.workers) < self.prev_workers + self.offer_count:
            self.salary *= 1.01
        else:
            self.salary *= 0.99
        self.price = 1.05 * self.salary/self.efficiency_coefficient
        self.price = self.price if self.price > 0 else 0
        return FirmLaborMarketAction(self.offer_count, self.salary, [])