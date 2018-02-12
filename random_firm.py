from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

import random

class RandomFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        self.type = 'RandomFirm'


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)

    def decide_salary(self, stats, firm):
        for parameter in firm.control_parameters:
            value = getattr(firm, parameter)
            if parameter in ['plan', 'labor_capacity', 'raw_need', 'capital_need']:
                firm.__setattr__(parameter, random.randint(value - value//3, value + value//3))
            else:
                firm.__setattr__(parameter, random.uniform(0.7 * value, 1.3 * value))

