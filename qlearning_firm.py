from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy
from .service import toStr, get_action_list

def argmax(two_dimensional_list, dimension):
    qs = numpy.array([q - min(two_dimensional_list[dimension]) for q in two_dimensional_list[dimension]])
    if sum(qs) == 0:
        qs = numpy.array([1 for q in two_dimensional_list[dimension]])
    indexes = [i for i in range(len(two_dimensional_list[dimension]))]
    arg_max = numpy.random.choice(indexes, replace = False, p = qs/sum(qs))
    return arg_max

class QlearningFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.actions = []
        for i in range(math.floor(math.pow(2, len(firm.control_parameters)))):
            action_list = get_action_list('{:0>2}'.format(toStr(i, 2)))
            action = ()
            for a, parameter in enumerate(firm.control_parameters):
                increment = 1
                if parameter in ['salary', 'price', 'salary_budget', 'raw_budget', 'capital_budget']:
                    increment = 0.01
                elif parameter == 'plan':
                    increment = firm.labor_productivity
                elif parameter == 'raw_need':
                    increment = firm.raw_productivity
                elif parameter == 'capital_need':
                    increment = firm.capital_productivity
                action = action + (action_list[a] * increment,)
            self.actions.append(action)
        self.action = self.actions[0]
        self.state = 0
        self.alpha = 0.5
        self.gamma = 0.5
        self.q = []
        for state in range(0, math.floor(math.pow(2, 2 + hasattr(firm, 'raw') + hasattr(firm, 'capital')))):
            self.q.append([])
            for action in self.actions:
                self.q[state].append(100)
        self.type = "QlearningFirm"

    def decide(self, stats, firm):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats, firm):
        self.update_state(firm)
        self.update(firm)
        self.action = self.actions[argmax(self.q, self.state)]
        for i, parameter in enumerate(firm.control_parameters):
            if parameter in ['salary', 'price', 'salary_budget', 'raw_budget', 'capital_budget']:
                firm.__setattr__(parameter, firm.__getattribute__(parameter) * (1 + self.action[i]))
            else:
                firm.__setattr__(parameter, firm.__getattribute__(parameter) + self.action[i])


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def update_state(self, firm):
        state = str(int(firm.sold < firm.plan)) + str(int(len(firm.workers) < firm.labor_capacity))
        if hasattr(firm, 'raw'):
            state += str(int(firm.raw < firm.raw_need))
        if hasattr(firm, 'capital'):
            state += str(int(firm.capital < firm.capital_need))
        self.state = int(state, base = 2)


    def update(self, firm):
        current_action = self.actions.index(self.action)
        self.q[self.state][current_action] = self.q[self.state][current_action] + self.alpha * (firm.profit + self.gamma * max(self.q[self.state]) - self.q[self.state][current_action])


