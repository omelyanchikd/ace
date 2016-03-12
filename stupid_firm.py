from firm import Firm
from firm_action import FirmAction


class StupidFirm(Firm):
    def decide(self):
        return FirmAction(0, 0, self.current_salary, 0, 0, 0, [])
