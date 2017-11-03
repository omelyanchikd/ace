from .household_history import HouseholdHistory

class Worker:
    def __init__(self, id, model_config, run_config):
        self.id = id
        self.step = 0
        self.salary = 0
        self.base_salary = 0
        self.employer = None
        self.productivity = 1
        self.unemployment_period = 0
        self.history = HouseholdHistory()
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is not None:
                setattr(self, parameter, run_config[parameter])
        self.income = 0
        if hasattr(self, 'consumption_need') or hasattr(self, 'consumption_budget'):
            self.f = 0.2
            self.savings_coefficient = 0.9
            self.consumption = 0
            self.consumption_expenses = 0



    def decide_consumption(self):
        self.income += self.salary
        self.step += 1
        self.money -= self.consumption_expenses
        self.history.add_record(self)
        if hasattr(self, 'consumption_budget'):
            self.consumption_budget = self.money - self.savings_coefficient * (self.money - self.f * self.income/
                                    self.step) if self.money > self.f * self.income/self.step else self.money
        if hasattr(self, 'consumption_need'):
            self.consumption_need = self.consumption_need + 1 if self.consumption == self.consumption_need else self.consumption_need
        self.consumption = 0
        self.consumption_expenses = 0




    # def work(self):
    #     print("I am a cool worker with id", self.id)
    #     if self.employer is not None:
    #         print("I am working for firm", self.employer, "with salary", self.salary)
    #     else:
    #         print("I am jobless, homeless and unhappy, so will work for food!")

