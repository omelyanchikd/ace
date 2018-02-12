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
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        self.price_regression = LinearRegression(normalize=True)
        self.price_x = [[200]]
        self.price_y = [20]
        self.salary_regression = LinearRegression(fit_intercept=False, normalize=True)
        self.salary_x = [[0]]
        self.salary_y = [0]
        self.raw_x = [[0]]
        self.raw_y = [0]
        self.capital_x = [[0]]
        self.capital_y = [0]
        self.raw_regression = LinearRegression()
        self.raw_regression.fit(numpy.array(self.raw_x), numpy.array(self.raw_y))
        self.capital_regression = LinearRegression()
        self.capital_regression.fit(numpy.array(self.capital_x), numpy.array(self.capital_y))
        self.type = "RationalFirm"
        self.prev_workers = len(firm.workers)

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        L = len(firm.workers)
        self.price_x.append([firm.sold])
        self.price_y.append(firm.price)
        self.price_regression.fit(numpy.array(self.price_x), numpy.array(self.price_y))
        self.salary_x.append([firm.salary])
        self.salary_y.append(L - self.prev_workers)
        self.salary_regression.fit(numpy.array(self.salary_x), numpy.array(self.salary_y))
        self.prev_workers = L
        alpha = firm.labor_productivity
        beta = 1
        gamma = 1
        delta = 0
        total_capital_expenses = 0
        if hasattr(firm, 'raw'):
            self.raw_x.append([firm.raw_bought])
            self.raw_y.append(firm.raw_expenses/firm.raw_bought)
            self.raw_regression.fit(numpy.array(self.raw_x), numpy.array(self.raw_y))
            beta = firm.raw_productivity
        if hasattr(firm, 'capital'):
            self.capital_x.append([firm.capital_bought])
            self.capital_y.append(firm.capital_expenses / firm.capital_bought)
            self.capital_regression.fit(numpy.array(self.capital_x), numpy.array(self.capital_y))
            gamma = firm.capital_productivity
            delta = firm.capital_amortization
            total_capital_expenses = firm.total_capital_expenses
        a = self.price_regression.intercept_
        b = self.price_regression.coef_[0]
        d = self.salary_regression.coef_[0]
        e = self.raw_regression.intercept_
        f = self.raw_regression.coef_[0]
        g = self.capital_regression.intercept_
        h = self.capital_regression.coef_[0]
        a0 = alpha * b - 1/d - math.pow(alpha, 2) * f/(math.pow(beta, 2)) - math.pow(alpha, 2) * delta * h/math.pow(gamma, 2)
        b0 = a - alpha* e/beta - alpha * delta * g/gamma + 2 * alpha * b * L - 2 * math.pow(alpha, 2) * f * L/math.pow(beta, 2) - \
            2 * math.pow(alpha, 2) * delta * h * L/math.pow(gamma, 2)
        c0 = a * L - alpha * e * L/beta - alpha * delta * g * L/gamma + alpha * b * math.pow(L, 2) - math.pow(alpha, 2) * f * math.pow(L, 2) /\
            math.pow(beta, 2) - math.pow(alpha, 2) * delta * h * math.pow(L, 2)/math.pow(gamma, 2) - firm.total_salary - delta * total_capital_expenses
        needed_workers = - 0.5 * b0/a0
        if a0 < 0:
            if math.ceil(needed_workers) + len(firm.workers) > 0:
                firm.plan = (len(firm.workers) + math.ceil(needed_workers)) * firm.labor_productivity
            else:
                firm.plan = firm.labor_productivity
        else:
            needed_workers = math.ceil(needed_workers)
            while a0 * math.pow(needed_workers, 2) + b0 * needed_workers + c0 <= 0 and needed_workers <= 0:
                needed_workers += 1
            firm.plan = math.ceil((len(firm.workers) + needed_workers) * firm.labor_productivity)
        #firm.plan = math.floor(random.uniform(0.8, 1.2) * 0.5 * (self.price_regression.intercept_ - self.raw_regression.intercept_/raw_productivity -
        #                   capital_amortization * self.capital_regression.intercept_/capital_productivity) / \
        #            (-self.price_regression.coef_[0] + 1/ (firm.labor_productivity * firm.labor_productivity* self.salary_regression.coef_[0]) +
        #             self.raw_regression.coef_[0]/(raw_productivity * raw_productivity) +
        #             capital_amortization * self.capital_regression.coef_[0]/(capital_productivity * capital_productivity)))
        firm.salary =  needed_workers / d if needed_workers > 0 else firm.salary
        control_parameters = ['plan', 'salary']
        if hasattr(firm, 'raw'):
            firm.raw_budget = (e + f * firm.plan/beta) * firm.plan/beta
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = (g + h * firm.plan / gamma) * firm.plan / gamma
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
