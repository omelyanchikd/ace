from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy

from sklearn.linear_model import LinearRegression


def rls(a, p, x, y):
    K = numpy.dot(p, x.T)/(numpy.dot(numpy.dot(x, p),x.T) + 1)
    a = a - K * (numpy.dot(x, a) - y)
    p = p - numpy.dot(K,numpy.dot(x, p))
    return a[0], a[1], p


class OligopolyFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.price_regression = LinearRegression()
        self.type = "OligopolyFirm"
        self.x = [[0]]
        self.y = [0]

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.x.append([-firm.sold])
        self.y.append(firm.price)
        self.price_regression.fit(numpy.array(self.x), numpy.array(self.y))
        net_cost = firm.total_salary
        if hasattr(firm, 'raw'):
            net_cost += firm.raw_expenses
        if hasattr(firm, 'capital'):
            net_cost += firm.capital_amortization * firm.capital_expenses
        net_cost = net_cost/firm.sold if firm.sold > 0 else net_cost/firm.plan
        firm.plan = math.floor(random.uniform(0.8, 1.2) * stats.firms * (self.price_regression.intercept_ - net_cost)/((stats.firms + 1) * self.price_regression.coef_[0]))
        firm.price = random.uniform(0.8, 1.2) * (self.price_regression.intercept_ + stats.firms * net_cost)/ (stats.firms + 1)
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