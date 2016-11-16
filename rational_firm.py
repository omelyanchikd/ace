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
    if len(a) == 2:
        return a[0], a[1], p
    return a[0], p


class RationalFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.a = 10000
        self.b = -50
        self.p1 = numpy.eye(2) * 10000
        self.p2 = [10000]
#       self.c = 0
        self.d = 0.25
        self.plan = 50 * self.efficiency_coefficient

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, self.sold]), self.price)
        self.d, self.p2 = rls(numpy.array([self.d]), self.p2, numpy.array([self.salary]), len(self.workers))
        self.plan = 0.5 * self.a / (-self.b + 1/ (self.efficiency_coefficient * self.efficiency_coefficient* self.d))
        self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.price = self.a + self.b * self.plan
        self.price = self.price if self.price > 0 else 0
        self.salary = self.plan / (self.d * self.efficiency_coefficient)
        self.salary = self.salary if self.salary > 0 else 0
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])