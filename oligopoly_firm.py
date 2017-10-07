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
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = firm.price
        self.a = 10000
        self.b = -50
        self.p1 = numpy.eye(2) * 10000
        self.type = "OligopolyFirm"

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, firm.sold]), firm.price)
        self.offer_count = math.floor(stats.firms * (self.a - firm.salary / firm.labor_productivity/((stats.firms + 1) * (-self.b * firm.labor_productivity))))- len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        firm.price = (self.a + stats.firms * firm.salary/firm.labor_productivity)/ (stats.firms + 1)
        firm.price = firm.price if firm.price > 0 else 0
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])