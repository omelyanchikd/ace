from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class IntuitiveFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.period = 3
        self.history = [1000, 1000, 1000]
        self.smoothing_coefficient = 0.5
        self.type = 'Extrapolation'

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)


    def decide_salary(self, stats, firm):
        if firm.sold >= firm.plan and firm.sold > 0:
            firm.plan = 1.1 *(self.smoothing_coefficient * firm.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history))
        else:
            firm.plan = self.smoothing_coefficient * firm.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history)
        self.history.append(firm.sold)
        self.history.pop(0)
        if len(firm.workers) < firm.labor_capacity:
            firm.salary *= 1.01
        else:
            firm.salary *= 0.99
        control_parameters = ['plan', 'salary']
        if hasattr(firm, 'raw'):
            firm.raw_budget = stats.raw_price * math.floor(firm.plan / firm.raw_productivity)
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = stats.capital_price * math.floor(firm.plan / firm.capital_productivity)
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            firm.__setattr__(parameter, firm.derive(parameter, control_parameters))

