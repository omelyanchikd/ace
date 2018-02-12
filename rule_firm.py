from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import random
import math
import numpy

def isinrange(value, left, right):
    return left <= value < right

def change(new_value, old_value):
    if isinstance(new_value, set):
        return (len(new_value) - len(old_value)) / len(old_value) if len(old_value) != 0 else 0
    return (new_value - old_value)/old_value if old_value != 0 else 0

def generate_sample_rule(rule_length):
    rule = []
    for i in range(rule_length + 1):
        left_limit = random.uniform(-0.3, 0.3)
        rule.append(left_limit)
        rule.append(random.uniform(left_limit, 0.3))

    return rule


class RuleFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id)

        self.external = ['price', 'sales', 'workers', 'sold', 'profit', 'world_unemployment_rate', 'world_salary', 'world_sales', 'world_sold']
        if hasattr(firm, 'raw'):
            self.external.append('raw')
        if hasattr(firm, 'capital'):
            self.external.append('capital')

        for parameter in self.external:
            if parameter == 'workers':
                setattr(self, 'previous_workers', len(firm.workers))
            elif hasattr(firm, parameter):
                setattr(self, 'previous_' + parameter, getattr(firm, parameter))
            else:
                setattr(self, 'previous_' + parameter, 0)

        for parameter in firm.control_parameters:
            setattr(self, 'hider_' + parameter, learning_data['hider_' + parameter])
        for parameter in ['world_unemployment_rate', 'world_salary', 'world_sales', 'world_sold']:
            setattr(self, 'hider_' + parameter, learning_data['hider_' + parameter])

        self.type = "RuleFirm"

    def decide_salary(self, stats, firm):
        current_state = []
        for parameter in self.external:
            if parameter == 'workers':
                change = (len(firm.workers) - getattr(self, 'previous_' + parameter)) / getattr(self,
                                                                                                'previous_' + parameter) \
                    if getattr(self, 'previous_' + parameter) != 0 else 0
                current_state.append(change)
                setattr(self, 'previous_' + parameter, len(firm.workers))
            elif hasattr(firm, parameter):
                current_state.append((getattr(firm, parameter) - getattr(self, 'previous_' + parameter)) / getattr(self,
                                                                                                                   'previous_' + parameter)
                                     if getattr(self, 'previous_' + parameter) != 0 else 0)
                setattr(self, 'previous_' + parameter, getattr(firm, parameter))
            else:
                #current_state.append(
                #    getattr(self, 'regression_' + parameter).predict(numpy.array(prediction_state).reshape(1, -1))[0])
                #current_state.append(self.get_parameter(parameter, current_state[:5]))
                current_state.append((getattr(stats, parameter.replace('world_', '')) - getattr(self, 'previous_' + parameter)) / getattr(self,
                                                                                                                   'previous_' + parameter)
                                     if getattr(self, 'previous_' + parameter) != 0 else 0)
                setattr(self, 'previous_' + parameter, getattr(stats, parameter.replace('world_', '')))

        for parameter in firm.control_parameters:
            value = getattr(firm, parameter)
            change = self.get_parameter(parameter, current_state)
            if parameter in ['plan', 'labor_capacity', 'raw_need', 'capital_need']:
                if firm.sold > 0:
                    firm.__setattr__(parameter, math.ceil(firm.sold * (1 + change)))
                else:
                    firm.__setattr__(parameter, math.ceil(firm.plan * (1 + change)))
            else:
                firm.__setattr__(parameter, value * (1 + self.get_parameter(parameter, current_state)))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def get_parameter(self, parameter, state):
        coverage = []
        rules = list(getattr(self, 'hider_' + parameter))
        for rule in rules:
            satisfies = 0
            for i in range(0, 2 * len(state), 2):
                if state[i//2] >= rule[i] and state[i//2] < rule[i+1]:
                    satisfies += 1
            if satisfies == len(state):
                return random.uniform(rule[len(rule) - 2], rule[len(rule) - 1])
            coverage.append(float(satisfies))
        if sum(coverage) > 0:
            select = numpy.random.choice([i for i in range(len(rules))], replace  = False, p = numpy.array(coverage) / sum(coverage))
        else:
            select = random.randrange(len(rules))
        return random.uniform(rules[select][len(rule) - 2], rules[select][len(rule) - 1])

    def update_state(self, firm):
        self.change = [change(getattr(firm, parameter), self.state[parameter]) for parameter in self.external]
        self.state = {parameter:getattr(firm, parameter) for parameter in self.external}


