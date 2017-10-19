from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_labormarket_action import FirmLaborMarketAction
from .firm_goodmarket_action import FirmGoodMarketAction

import math
import random


class DianaFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.prev_price = 1000
        self.type = 'DianaFirm'

    def decide_salary(self, stats, firm):
        price_increase = self.prev_price < firm.price
        already_decreased = False
        self.prev_price = firm.price
        if firm.sold >= firm.plan:
            firm.plan = firm.sold + math.floor(firm.labor_productivity)
            firm.price *= 1.05
        else:
            firm.price *= 0.95
            #if price_increase:
            #    self.price *= 0.95
            #    already_decreased = True
            #else:
            #    self.plan = self.sold if self.sold > 0 else self.efficiency_coefficient
        control_parameters = ['plan', 'price']
        if hasattr(firm, 'raw'):
            firm.raw_budget = stats.raw_price * math.floor(firm.plan / firm.raw_productivity)
            control_parameters.append('raw_budget')
        if hasattr(firm, 'capital'):
            firm.capital_budget = stats.capital_price * (math.floor(firm.plan / firm.capital_productivity) - firm.capital)
            control_parameters.append('capital_budget')
        for parameter in firm.control_parameters:
            firm.__setattr__(parameter, firm.derive(parameter, control_parameters))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
