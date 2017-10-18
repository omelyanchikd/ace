from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import random
import math

def isinrange(value, left, right):
    return left <= value < right

def change(new_value, old_value):
    return (new_value - old_value)/old_value if old_value != 0 else 0

def generate_sample_rule(rule_length):
    return [random.uniform(-1, 1) for i in range(rule_length * 2 + 2)]


class RuleFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)

        self.external = ['sales', 'sold', 'profit', 'workers']
        if hasattr(firm, 'raw'):
            self.external.append('raw')
        if hasattr(firm, 'capital'):
            self.external.append('capital')

        rules_n = 10

        for parameter in firm.parameters:
            setattr(self, 'rules_' + parameter, [generate_sample_rule(len(self.external)) for i in range(rules_n)])

        self.change = [0] * len(self.external)
        self.state = {parameter: getattr(firm, parameter) for parameter in self.external}

        self.type = "RuleFirm"

    def decide_salary(self, stats, firm):
        self.update_state(firm)

        for parameter in firm.control_parameters:
            value = getattr(firm, parameter)
            if parameter in ['plan', 'labor_capacity', 'raw_need', 'capital_need']:
                firm.__setattr__(parameter, math.floor(value * (1 + self.get_parameter(getattr(self, 'rules_' + parameter), self.change))))
            else:
                firm.__setattr__(parameter, value * (1 + self.get_parameter(getattr(self, 'rules_' + parameter), self.change)))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def get_parameter(self, rules, state):
        for rule in rules:
            for i in range(0, 2 * len(state), 2):
                if state[i//2] < rule[i] or state[i//2] >= rule[i+1]:
                    break
            if i == 2 * len(state):
                return random.uniform(rule[2 * len(state)], rule[2 * len(state) + 1])
        select = random.randint(0, len(rules) - 1)
        return random.uniform(rules[select][2 * len(state)], rules[select][2 * len(state) + 1])

    def update_state(self, firm):
        self.change = [change(getattr(firm, parameter), self.state[parameter]) for parameter in self.external]
        self.state = {parameter:getattr(firm, parameter) for parameter in self.external}


