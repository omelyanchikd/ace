from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random


class DianaFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.plan = 50 * self.efficiency_coefficient
        self.prev_price = 0
        self.salary = 200
        self.offer_count = 0
        self.type = 'DianaFirm'

    def decide_salary(self, stats):
        if self.sold >= self.plan and self.sold > 0:
            self.plan = self.sold + math.floor(self.efficiency_coefficient)
            self.prev_price = self.price
            self.price *= 1.05
        else:
            if self.prev_price < self.price:
                self.prev_price = self.price
                self.price *= 0.95
            else:
                self.plan = self.sold
        self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = self.plan // self.efficiency_coefficient- len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        total_salary = sum([worker.salary for worker in self.workers])
        self.salary = 0.95 * (self.price * len(self.workers) * self.efficiency_coefficient -
                              total_salary)/self.offer_count if self.offer_count > 0 else self.salary
        self.labor_capacity = self.offer_count + len(self.workers)
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)
