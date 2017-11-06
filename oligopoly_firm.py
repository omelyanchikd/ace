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
    return a[0], a[1], p


class OligopolyFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.a = 10000
        self.b = -50
        self.p1 = numpy.eye(2) * 10000
        self.type = "OligopolyFirm"

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.a, self.b, self.p1 = rls(numpy.array([self.a, self.b]), self.p1, numpy.array([1, firm.sold]), firm.price)
        net_cost = firm.total_salary
        if hasattr(firm, 'raw'):
            net_cost += firm.raw_expenses
        if hasattr(firm, 'capital'):
            net_cost += firm.capital_amortization * firm.capital_expenses
        net_cost /= firm.plan
        firm.plan = math.floor(stats.firms * (self.a - net_cost)/((stats.firms + 1) * (-self.b)))
        firm.price = (self.a + stats.firms * net_cost)/ (stats.firms + 1)
        control_parameters = ['plan', 'price']
        if hasattr(firm, 'raw'):
            firm.raw_budget = stats.raw_price * firm.plan / firm.raw_productivity
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = stats.capital_price * (firm.plan / firm.capital_productivity - firm.capital)
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))