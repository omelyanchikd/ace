from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import math
import random


class DianaFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        self.prev_price = 1000
        self.type = 'DianaFirm'

    def decide_salary(self, stats, firm):
        price_increase = self.prev_price < firm.price
        already_decreased = False
        self.prev_price = firm.price
        if firm.stock <= 0:
            firm.plan = firm.sold + math.floor(firm.labor_productivity)
            firm.price *= 1.05
        else:
            if price_increase:
                firm.price *= 0.95
            else:
                firm.plan = firm.sold if firm.sold > 0 else firm.labor_productivity
        self.prev_price = firm.price
        control_parameters = ['plan', 'price']
        if hasattr(firm, 'raw'):
            firm.raw_budget = stats.raw_price * firm.plan / firm.raw_productivity
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = stats.capital_price * (firm.plan / firm.capital_productivity)
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))
        for parameter in firm.derived_parameters:
            if parameter not in control_parameters:
                firm.__setattr__(parameter, firm.derive(parameter, control_parameters))



    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
