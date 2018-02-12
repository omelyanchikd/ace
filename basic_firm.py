from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction


class BasicFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id, firm, learning_data)
        self.type = 'BasicFirm'

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        self.labor_capacity = len(self.workers) + 1
        return FirmLaborMarketAction(1, self.current_salary, [])
