from firm import Firm
from firm_action import FirmAction


class RuleFirm():
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.salary_change = 0
        self.price_change = 0
        self.production_change = 0
