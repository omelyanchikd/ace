from firm import Firm
from firm_action import FirmAction


class DianaFirm(Firm):
    def __init__(self, id):
        super().__init__(id)

    def decide(self):
        offer_count = 5
        salary = 200
        production_count = self.stock
        workers = len(self.workers) + offer_count
        efficiency = self.efficiency_coefficient
        price = salary / efficiency * 0.99

        return FirmAction(offer_count, salary, production_count, price, 0, 0, [])
