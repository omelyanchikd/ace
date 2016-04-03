from firm import Firm
from firm_action import FirmAction
from firm_result import FirmResult


class SuperFirm(Firm):
    salary_step = 50
    price_step = 50

    def __init__(self, id):
        super().__init__(id)
        # self.current_salary = 2000
        self.actions = []
        self.plan = FirmAction(50, self.current_salary, self.stock, 10, 0, 0, [])
        self.last_result = None

    def rethink(self):
        self.plan.production_count = self.stock
        if self.last_result is None:
            return
        if len(self.last_result.new_workers) > 0:
            self.plan.salary -= self.salary_step
        else:
            self.plan.salary += self.salary_step
        if self.last_result.sold_count < self.plan.offer_count:
            self.plan.price -= self.price_step
            # else:
            #     self.plan.price += self.price_step

    def decide(self):
        self.rethink()
        action = self.plan
        self.actions.append(action)
        return action

    def apply_result(self, result: FirmResult):
        super().apply_result(result)
        self.last_result = result
