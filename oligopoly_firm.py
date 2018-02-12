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
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        self.price_regression = LinearRegression()
        self.costs_regression = LinearRegression()
        self.type = "OligopolyFirm"
        self.price_x = [[200]]
        self.price_y = [20]
        self.costs_x = [[2000]]
        self.costs_y = [40000]

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.price_x.append([firm.sold])
        self.price_y.append(firm.price)
        self.price_regression.fit(numpy.array(self.price_x), numpy.array(self.price_y))
        total_costs = firm.total_salary
        if hasattr(firm, 'raw'):
            total_costs += firm.raw_expenses
        if hasattr(firm, 'capital'):
            total_costs += firm.capital_amortization * firm.total_capital_expenses
        self.costs_x.append([firm.sold + firm.stock])
        self.costs_y.append(total_costs)
        self.costs_regression.fit(numpy.array(self.costs_x), numpy.array(self.costs_y))
        firm.plan = math.ceil((-self.price_regression.intercept_ - self.costs_regression.coef_[0])/((stats.firms + 1) * self.price_regression.coef_[0]))
        firm.price = (-self.price_regression.intercept_ + stats.firms * self.costs_regression.coef_[0])/ (stats.firms + 1)
        control_parameters = ['plan', 'price']
        if hasattr(firm, 'raw'):
            firm.raw_budget = stats.raw_price * firm.plan / firm.raw_productivity
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = stats.capital_price * (firm.plan / firm.capital_productivity - firm.capital)
            control_parameters.append('capital_budget')
        for worker in list(firm.workers):
            firm.fire_worker(worker)
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))