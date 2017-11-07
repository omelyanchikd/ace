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
    if len(a) == 2:
        return a[0], a[1], p
    return a[0], p


class RationalFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.price_regression = LinearRegression(normalize=True)
        self.a = [[-10]]
        self.b = [100]
        self.salary_regression = LinearRegression(fit_intercept=False, normalize=True)
        self.c = [[0]]
        self.d = [0]
        self.e = [[0]]
        self.f = [0]
        self.g = [[0]]
        self.h = [0]
        self.raw_regression = LinearRegression()
        self.raw_regression.fit(numpy.array(self.e), numpy.array(self.f))
        self.capital_regression = LinearRegression()
        self.capital_regression.fit(numpy.array(self.g), numpy.array(self.h))
        self.type = "RationalFirm"

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.a.append([-firm.sold])
        self.b.append(firm.price)
        self.price_regression.fit(numpy.array(self.a), numpy.array(self.b))
        self.c.append([firm.salary])
        self.d.append(len(firm.workers))
        self.salary_regression.fit(numpy.array(self.c), numpy.array(self.d))
        raw_productivity = 1
        capital_productivity = 1
        capital_amortization = 1
        if hasattr(firm, 'raw'):
            self.e.append([-firm.raw_bought])
            self.f.append(firm.raw_expenses/firm.raw_bought)
            self.raw_regression.fit(numpy.array(self.e), numpy.array(self.f))
            raw_productivity = firm.raw_productivity
        if hasattr(firm, 'capital'):
            self.g.append([-firm.capital_bought])
            self.h.append(firm.capital_expenses / firm.capital_bought)
            self.capital_regression.fit(numpy.array(self.g), numpy.array(self.h))
            capital_productivity = firm.capital_productivity
            capital_amortization = firm.capital_amortization
        a0 = firm.labor_productivity * firm.labor_productivity * self.price_regression.coef_[0]
        b0 = firm.labor_productivity * self.price_regression.intercept_ + 2 * self.price_regression.coef_[0] * math.pow(firm.labor_productivity, 2) *\
            len(firm.workers) - len(firm.workers)/self.salary_regression.coef_[0]
        c0 = firm.labor_productivity * self.price_regression.intercept_ * len(firm.workers) + math.pow(firm.labor_productivity, 2) *\
            self.price_regression.coef_[0] * math.pow(len(firm.workers), 2) - firm.total_salary
        needed_workers = - 0.5 * b0/a0
        if a0 > 0:
            if needed_workers >= 0:
                firm.plan = (len(firm.workers) + needed_workers) * firm.labor_productivity
            else:
                while a0 * math.pow(needed_workers, 2) + b0 * needed_workers + c0  < 0:
                    needed_workers += 1
        else:
            needed_workers = needed_workers if needed_workers + len(firm.workers) > 0 else 0
        firm.plan = math.floor((len(firm.workers) + needed_workers) * firm.labor_productivity * random.uniform(0.8, 1.2))
        #firm.plan = math.floor(random.uniform(0.8, 1.2) * 0.5 * (self.price_regression.intercept_ - self.raw_regression.intercept_/raw_productivity -
        #                   capital_amortization * self.capital_regression.intercept_/capital_productivity) / \
        #            (-self.price_regression.coef_[0] + 1/ (firm.labor_productivity * firm.labor_productivity* self.salary_regression.coef_[0]) +
        #             self.raw_regression.coef_[0]/(raw_productivity * raw_productivity) +
        #             capital_amortization * self.capital_regression.coef_[0]/(capital_productivity * capital_productivity)))
        firm.salary = random.uniform(0.8, 1.2) *  firm.plan / (self.salary_regression.coef_[0] * firm.labor_productivity)
        control_parameters = ['plan', 'salary']
        if hasattr(firm, 'raw'):
            firm.raw_budget = (self.raw_regression.intercept_ + self.raw_regression.coef_[0] * firm.plan/raw_productivity) * firm.plan/raw_productivity
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = (self.capital_regression.intercept_ + self.capital_regression.coef_[0] * firm.plan / capital_productivity) * firm.plan / capital_productivity
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
