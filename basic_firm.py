from firm import Firm
from firm_action import FirmAction


class BasicFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.current_salary = 2000

    def decide(self):
        self.current_salary = 2000
        return FirmAction(500, self.current_salary, self.stock, 10, 0, 0, [])
