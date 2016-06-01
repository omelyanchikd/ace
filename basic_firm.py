from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction


class BasicFirm(Firm):
    def __init__(self, id):
        super().__init__(id)

    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        return FirmLaborMarketAction(1, self.current_salary, [])
