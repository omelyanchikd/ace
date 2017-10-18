from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

from sklearn.svm import SVC

from sklearn import tree

import numpy
import random
import math

class SvmFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.svm = SVC()
        self.world_history = []
        self.profit_history = []
        self.type = "SvmFirm"

    def update_history(self, stats, firm, type):
        self.world_history.append(firm.control_parameters + [getattr(stats, type + '_price'), getattr(stats, type + '_salary')])
        self.profit_history.append(1 if firm.profit > 0 else 0)

    def generate_parameters(self, stats, firm, type):
        new_parameters = [getattr(firm, parameter) for parameter in firm.control_parameters]
        trial_parameters = []
        for parameter in new_parameters:
            change = random.gauss(0, 1)
            parameter *= (1 + change)
            trial_parameters.append(parameter)
        #trial_parameters.append(math.ceil(new_parameters[2] / self.efficiency_coefficient))
        for parameter in [getattr(stats, type + '_price'), getattr(stats, type + '_salary')]:
            trial_parameters.append(parameter)
        return new_parameters, trial_parameters


    def decide_salary(self, stats, firm):
        type = firm.type[:len(firm.type) - 4].lower()
        self.update_history(stats, firm, type)
        current_data = firm.control_parameters + [getattr(stats, type + '_price'), getattr(stats, type + '_salary')]
        if len(set(self.profit_history)) == 2:
            self.svm.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats, firm, type)
            if len(set(self.profit_history)) == 2:
                has_profit = self.svm.predict(trial_parameters)
            else:
                has_profit = random.randint(0,1)
            if has_profit == 1:
                new_parameters = trial_parameters[:len(firm.control_parameters)]
                break
        for i, parameter in enumerate(firm.control_parameters):
            setattr(firm, parameter, new_parameters[i])


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
