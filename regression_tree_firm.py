from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

from sklearn.tree import DecisionTreeRegressor

import numpy
import random
import math
import pandas

def change(new_value, old_value):
    return (new_value - old_value)/old_value if old_value != 0 else 0

def generate_sample_data(sample_size):
    return [random.uniform(-1, 1) for i in range(sample_size + 1)]


class RegressionTreeFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)

        self.external = ['sales', 'sold', 'profit', 'workers']
        if hasattr(firm, 'raw'):
            self.external.append('raw')
        if hasattr(firm, 'capital'):
            self.external.append('capital')

        sample_size = 1000

        for parameter in firm.control_parameters:
            setattr(self, 'sample_' + parameter, [generate_sample_data(len(self.external)) for i in range(sample_size)])
            setattr(self, 'regression_' + parameter, DecisionTreeRegressor(max_depth=5))
            getattr(self, 'regression_' + parameter).fit([getattr(self, 'sample_' + parameter)[:len(self.external) - 1]
            for i in range(sample_size)], [getattr(self, 'sample_' + parameter)[len(self.external) - 1] for i in range(sample_size)])



        self.change = [0] * len(self.external)
        self.state = {parameter: getattr(firm, parameter) for parameter in self.external}

        self.type = "RuleFirm"

    def decide_salary(self, stats, firm):
        self.update_state(firm)

        for parameter in firm.control_parameters:
            value = getattr(firm, parameter)
            if parameter in ['plan', 'labor_capacity', 'raw_need', 'capital_need']:
                firm.__setattr__(parameter, math.floor(value * (1 + self.regression.predict(self.change))))
            else:
                firm.__setattr__(parameter, value * (1 + self.regression.predict(self.change)))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)


    def update_state(self, firm):
        self.change = [change(getattr(firm, parameter), self.state[parameter]) for parameter in self.external]
        self.state = {parameter:getattr(firm, parameter) for parameter in self.external}