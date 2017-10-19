from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction
from .service import get_action_list, toStr

import random
import math
import numpy

def transform(x):
    return 2/math.pi * math.atan(x/500000)

def update(probabilities, reward, action):
    new_probabilities = probabilities
    if reward != 0:
        print(transform(reward))
    if reward < 0:
        for i in range(0, len(probabilities)):
            if i == action:
                new_probabilities[i] = probabilities[i] - transform(-reward) * probabilities[i]
            else:
                new_probabilities[i] = probabilities[i] + transform(-reward) * probabilities[i] * probabilities[action] /(1 - probabilities[action])
    elif reward > 0:
        for i in range(0, len(probabilities)):
            if i == action:
                new_probabilities[i] = probabilities[i] + transform(reward) * (1 - probabilities[i])
            else:
                new_probabilities[i] = probabilities[i] - transform(reward) * probabilities[i]
    return new_probabilities


class BudgetFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.shares = ['salary_budget_share']
        self.salary_budget_share = 0
        if hasattr(self, 'raw'):
            self.raw_budget_share = 0
            self.shares.append('raw_budget_share')
        if hasattr(self, 'capital'):
            self.capital_budget_share = 0
            self.shares.append('capital_budget_share')
        for share in self.shares:
            setattr(self, share, 1/(len(self.shares) + 1))
        self.probabilities = [1 / math.pow(3, len(self.shares))] * math.floor(math.pow(3, len(self.shares)))
        self.actions = []
        for i in range(len(self.probabilities)):
            action_list = get_action_list('{:0>3}'.format(toStr(i, 3)))
            action = ()
            for a, parameter in enumerate(self.shares):
                increment = 0.01
                action = action + (action_list[a] * increment,)
            self.actions.append(action)
        self.action = self.actions[0]
        self.type = 'BudgetFirm'


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        self.probabilities = update(self.probabilities, firm.profit, self.actions.index(self.action))
        distribution = numpy.array(self.probabilities)
        indexes = [i for i in range(0, len(self.probabilities))]
        self.action = self.actions[numpy.random.choice(indexes, replace = False, p = distribution/sum(distribution))]
        for i, parameter in enumerate(self.shares):
            self.__setattr__(parameter, self.__getattribute__(parameter) * (1 + self.action[i]))
            value = firm.sales if firm.sales > 0 else firm.money
            firm.__setattr__(parameter.replace('_share', ''), value * self.__getattribute__(parameter))
        firm.labor_capacity = len(firm.workers) + math.floor((firm.salary_budget - firm.total_salary)/firm.salary) if firm.salary > 0 else 0
        control_parameters = self.shares + ['labor_capacity']
        for parameter in firm.control_parameters:
            firm.__setattr__(parameter, firm.derive(parameter, control_parameters))



