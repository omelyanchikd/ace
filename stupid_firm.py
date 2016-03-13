from firm import Firm
from firm_action import FirmAction


class StupidFirm(Firm):
    def decide(self):
        return FirmAction(1, 200, self.stock, self.price, 0, 0, [])
