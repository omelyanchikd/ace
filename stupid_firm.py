from firm import Firm
from firm_action import FirmAction


class StupidFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
    def decide(self):
        return FirmAction(1, self.current_salary, self.stock, self.price, 0, 0, [])
