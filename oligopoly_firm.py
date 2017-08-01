from decision_maker import DecisionMaker
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
    return a[0], a[1], p


class OligopolyFirm(DecisionMaker):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.a = 10000
        self.b = -50
        self.p1 = numpy.eye(2) * 10000
        self.type = "OligopolyFirm"

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, self.sold]), self.price)
        self.offer_count = math.floor(stats.f * (self.a - self.salary / self.efficiency_coefficient/((stats.f + 1) * (-self.b * self.efficiency_coefficient))))- len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.price = (self.a + stats.f * self.salary/self.efficiency_coefficient)/ (stats.f + 1)
        self.price = self.price if self.price > 0 else 0
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])