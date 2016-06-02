from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

class MosesFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200

    def decide_salary(self, stats):
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)