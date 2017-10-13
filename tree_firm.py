from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

from sklearn import tree
from sklearn.linear_model import Perceptron
from sklearn.neural_network import MLPClassifier

import numpy
import random
import math
import pandas

class TreeFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.type = 'TreeFirm'
        self.salary = firm.salary
        #recorded_history = pandas.read_csv("change_history.csv", sep = ";", decimal = ",")
        #self.world_history = recorded_history.as_matrix(columns = ['price', 'salary', 'sold', 'workers', 'world_price', 'world_salary',
        #                                                           'rest_money', 'world_sold'])
        #self.world_history = self.world_history.tolist()
        #self.profit_history = list(recorded_history['has_profit'])
        self.decision_tree = tree.DecisionTreeClassifier()
        self.world_history = []
        self.profit_history = []
        #self.decision_tree.fit(self.world_history, self.profit_history)

#        self.prev_state = [19.9, 199.9, 500, 50, 20, 200, 0, 5000]
#        self.current_state = [] * 8
#        self.change = [] * 8

    def update_history(self, stats, firm, type):
#        self.current_state = [firm.price, firm.salary, firm.sold, len(firm.workers), stats.price, stats.salary,
#                              stats.money - stats.sales, stats.sold]
#        self.change = [(self.current_state[i] - self.prev_state[i])/self.prev_state[i] if self.prev_state[i] != 0 else 0 for i in range(0, len(self.prev_state)) ]
#        self.prev_state = [firm.price, firm.salary, firm.sold, len(firm.workers), stats.price, stats.salary,
#                           stats.money - stats.sales, stats.sold]

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
            self.decision_tree.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats, firm, type)
            if len(set(self.profit_history)) == 2:
                has_profit = self.decision_tree.predict(trial_parameters)
            else:
                has_profit = random.randint(0,1)
            if has_profit == 1:
                new_parameters = trial_parameters[:len(firm.control_parameters)]
                break
        for i, parameter in enumerate(firm.control_parameters):
            setattr(firm, parameter, new_parameters[i])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
