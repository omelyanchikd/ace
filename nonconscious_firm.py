from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy



def toStr(n, base):
   convertString = "0123456789ABCDEF"
   if n < base:
      return convertString[n]
   else:
      return toStr(n//base,base) + convertString[n % base]


def get_action_list(action):
    action_list = []
    action_dict = {'0': 0, '1': 1, '2': -1}
    for c in action:
        action_list.append(action_dict[c])
    return action_list

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


class NonconsciousFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.offer_count = 0
        self.probabilities = [1/math.pow(3, len(firm.control_parameters))] * math.floor(math.pow(3, len(firm.control_parameters)))
        self.actions = []
        for i in range(len(self.probabilities)):
            action_list = get_action_list('{:0>3}'.format(toStr(i, 3)))
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
        self.type = "NonconsciousFirm"

    def decide(self, stats, firm):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats, firm):
        self.probabilities = update(self.probabilities, firm.sold * firm.profit/firm.price, self.actions.index(self.action))
        distribution = numpy.array(self.probabilities)
        indexes = [i for i in range(0, len(self.probabilities))]
        self.action = self.actions[numpy.random.choice(indexes, replace = False, p = distribution/sum(distribution))]
        for i, parameter in enumerate(firm.control_parameters):
            if parameter in ['salary', 'price', 'salary_budget', 'raw_budget', 'capital_budget']:
                firm.__setattr__(parameter, firm.__getattribute__(parameter) * (1 + self.action[i]))
            else:
                firm.__setattr__(parameter, firm.__getattribute__(parameter) + self.action[i])
        for parameter in firm.derived_parameters:
            firm.__setattr__(parameter, firm.derive(parameter, firm.control_parameters))
        return FirmLaborMarketAction(firm.labor_capacity - len(firm.workers), firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
