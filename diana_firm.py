from firm import Firm
from firm_action import FirmAction

import math


class DianaFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.plan = 50 * self.efficiency_coefficient
        self.prev_price = 0
        self.salary = 200

    def decide(self, stats):
        if self.sold >= self.plan:
            self.plan += math.floor(self.efficiency_coefficient)
            self.prev_price = self.price
            self.price *= 1.05
        else:
            if self.prev_price < self.price:
                self.prev_price = self.price
                self.price *= 0.95
            else:
                self.plan = self.sold
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        self.salary = 1.05 * self.price * self.efficiency_coefficient
        return FirmAction(self.offer_count, self.salary, self.stock, self.price, 0, 0, [])
