from .outside_world_history import OutsideWorldHistory

class OutsideWorld:

    def __init__(self, run_config):
        for parameter in run_config:
            setattr(self, parameter, run_config[parameter])
        self.id = "OutsideWorld"
        self.step = 0
        self.raw_sales = 0
        self.raw_expenses = 0
        self.raw_sold = 0
        self.raw_bought = 0
        self.capital_sales = 0
        self.capital_expenses = 0
        self.capital_sold = 0
        self.capital_bought = 0
        self.production_sales = 0
        self.production_expenses = 0
        self.production_sold = 0
        self.production_bought = 0
        self.history = OutsideWorldHistory()

    def update(self):
        self.history.add_record({variable: getattr(self, variable) for variable in self.__dict__.items() if variable != 'id'})
        self.step += 1
        self.raw_sales = 0
        self.raw_expenses = 0
        self.raw_sold = 0
        self.raw_bought = 0
        self.capital_sales = 0
        self.capital_expenses = 0
        self.capital_sold = 0
        self.capital_bought = 0
        self.production_sales = 0
        self.production_expenses = 0
        self.production_sold = 0
        self.production_bought = 0





