from firm import Firm
from firm_action import FirmAction


class BasicFirm(Firm):
    def decide(self):
        return FirmAction(500, 2000, self.stock, 10, 0, 0, [])
