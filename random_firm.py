from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random

class RandomFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.type = 'RandomFirm'



    def decide_price(self, stats):
        self.price = random.uniform(10, 30)
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        self.salary = random.uniform(150, 250)
        self.labor_capacity = len(self.workers) + 1
        return FirmLaborMarketAction(1, self.salary, [])
