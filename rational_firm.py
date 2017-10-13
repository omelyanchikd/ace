from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

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


class RationalFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = firm.salary
        self.a = 10000
        self.b = -50
        self.p1 = numpy.eye(2) * 10000
        self.p2 = [10000]
#       self.c = 0
        self.d = 0.25
        self.plan = 50 * firm.labor_productivity
        self.type = "RationalFirm"

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, firm.sold]), firm.price)
        self.d, self.p2 = rls(numpy.array([self.d]), self.p2, numpy.array([firm.salary]), len(firm.workers))
        firm.plan = 0.5 * self.a / (-self.b + 1/ (firm.labor_productivity * firm.labor_productivity* self.d))
        firm.plan = (firm.plan - firm.stock) // firm.labor_productivity * firm.labor_productivity
        firm.plan = firm.plan if firm.plan >= 0 else 0
        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        firm.price = self.a + self.b * firm.plan
        firm.price = firm.price if firm.price > 0 else 0
        firm.salary = firm.plan / (self.d * firm.labor_productivity)
        firm.salary = firm.salary if firm.salary > 0 else 0
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])