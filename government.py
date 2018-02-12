import math

from .government_history import GovernmentHistory

class Government:

    def __init__(self, model_config, run_config):
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is not None:
                setattr(self, parameter, run_config[parameter])
        self.history = GovernmentHistory()


    def get_profit_tax(self, firms):
        for firm in firms:
            profit_tax = self.profit_tax * firm.profit if firm.profit > 0 else 0
            firm.money -= profit_tax
            firm.profit -= profit_tax
            self.money += profit_tax
            self.history.add_record({'step': firm.step,
                                     'participant_id': firm.id,
                                     'action': 'profit_tax',
                                     'money': profit_tax,
                                     'tax': self.profit_tax})

    def get_income_tax(self, households):
        for household in households:
            income_tax = self.income_tax * household.salary if household.employer is not None else 0
            household.money -= income_tax
            self.money += income_tax
            self.history.add_record({'step': household.step,
                                     'participant_id': household.id,
                                     'action': 'income_tax',
                                     'money': income_tax,
                                     'tax': self.income_tax})

    def get_import_tax(self, step, transaction):
        self.money += self.import_tax * transaction
        self.history.add_record({'step': step,
                                 'participant_id': 'OustsideWorld',
                                 'action': 'import_tax',
                                 'money': self.import_tax * transaction,
                                 'tax': self.import_tax})



    def provide_help(self, households):
        for household in households:
            if household.employer is None:
                household.unemployment_period += 1
                help = household.base_salary * math.pow(self.coefficient_help, household.unemployment_period - 1)
                help = help if help > self.minimal_help else self.minimal_help
                self.money -= help
                household.money += help
                self.history.add_record({'step': household.step,
                                         'participant_id': household.id,
                                         'action': 'help',
                                         'money': help,
                                         'tax': self.coefficient_help})




