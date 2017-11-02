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
        self.e = 0
        self.f = 0
        self.g = 0
        self.h = 0
        if hasattr(firm, 'raw'):
            self.e = 10000
            self.f = - 50
            self.p3 = numpy.eye(2) * 10000
        if hasattr(firm, 'capital'):
            self.g = 10000
            self.h = - 50
            self.p4 = numpy.eye(2) * 10000

        self.type = "RationalFirm"

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, firm.sold]), firm.price)
        self.d, self.p2 = rls(numpy.array([self.d]), self.p2, numpy.array([firm.salary]), len(firm.workers))
        raw_productivity = 1
        capital_productivity = 1
        capital_amortization = 1
        if hasattr(firm, 'raw'):
            self.e, self.f, self.p3 = rls(numpy.array([self.e, self.f]), self.p3, numpy.array([1, firm.raw]),
                                          stats.price)
            raw_productivity = firm.raw_productivity
        if hasattr(firm, 'capital'):
            self.g, self.h, self.p4 = rls(numpy.array([self.g, self.h]), self.p4, numpy.array([1, firm.capital]),
                                          stats.price)
            capital_productivity = firm.capital_productivity
            capital_amortization = firm.capital_amortization
        firm.plan = 0.5 * (self.a - self.e/raw_productivity - capital_amortization * self.g/capital_productivity) / \
                    (- self.b + 1/ (firm.labor_productivity * firm.labor_productivity* self.d) + self.f/(raw_productivity * raw_productivity) +
                     capital_amortization * self.h/(capital_productivity * capital_productivity))
        firm.salary = firm.plan / (self.d * firm.labor_productivity)
        control_parameters = ['plan', 'salary']
        if hasattr(firm, 'raw'):
            firm.raw_budget = (self.e + self.f * firm.plan/raw_productivity) * firm.plan/raw_productivity
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = (self.g + self.h * firm.plan / capital_productivity) * firm.plan / capital_productivity
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
