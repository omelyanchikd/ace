from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


def rls(a, p, x, y):
    K = numpy.dot(p, x.T)/(numpy.dot(numpy.dot(x, p),x.T) + 1)
    a = a - K * (numpy.dot(x, a) - y)
    p = p - numpy.dot(K,numpy.dot(x, p))
    return a, p


class RationalFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.a = 100
        self.b = -100
        self.p1 = 1000
        self.p2 = 1000
        self.c = 100
        self.d = 100
        self.plan = 50 * self.efficiency_coefficient

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        ab = []
        ab.append(self.a)
        ab.append(self.b)
        cd = []
        cd.append(self.c)
        cd.append(self.d)
        self.a, self.b, self.p1 = rls(numpy.array(ab), self.p1, self.sold, self.price)
        self.c, self.d, self.p2 = rls(numpy.array(cd), self.p1, self.salary, len(self.workers))
        self.plan = 0.5 * self.efficiency_coefficient * (self.efficiency_coefficient * self.a * self.d + self.c) / (1 +
                self.b * self.a * self.efficiency_coefficient * self.efficiency_coefficient)
        self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.price = self.a - self.b * self.plan
        self.price = self.price if self.price > 0 else 0
        self.salary = (self.plan - self.efficiency_coefficient * self.c) / (self.a * self.efficiency_coefficient)
        self.salary = self.salary if self.salary > 0 else 0
        return FirmLaborMarketAction(self.offer_count, self.salary, [])