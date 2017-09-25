from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

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
        recorded_history = pandas.read_csv("change_history.csv", sep = ";", decimal = ",")
        self.world_history = recorded_history.as_matrix(columns = ['price', 'salary', 'sold', 'workers', 'world_price', 'world_salary',
                                                                   'rest_money', 'world_sold'])
        self.world_history = self.world_history.tolist()
        self.profit_history = list(recorded_history['has_profit'])
        self.decision_tree = tree.DecisionTreeClassifier()
        self.decision_tree.fit(self.world_history, self.profit_history)
        #self.neural_network = Perceptron(fit_intercept=False)
        #self.neural_network.fit(self.world_history, self.profit_history)
        #self.neural_network = MLPClassifier(hidden_layer_sizes=(30, ))
        #self.neural_network.fit(self.world_history, self.profit_history)
        self.plan = firm.plan
        self.offer_count = 0
        self.prev_state = [19.9, 199.9, 500, 50, 20, 200, 0, 5000]
        self.current_state = [] * 8
        self.change = [] * 8

    def update_history(self, stats, firm):
        self.current_state = [firm.price, firm.salary, firm.sold, len(firm.workers), stats.price, stats.salary,
                              stats.money - stats.sales, stats.sold]
        self.change = [(self.current_state[i] - self.prev_state[i])/self.prev_state[i] if self.prev_state[i] != 0 else 0 for i in range(0, len(self.prev_state)) ]
        self.prev_state = [firm.price, firm.salary, firm.sold, len(firm.workers), stats.price, stats.salary,
                           stats.money - stats.sales, stats.sold]

        #self.world_history.append([self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
        #                           stats.money - stats.sales, stats.employed, stats.sold])

        self.world_history.append(self.change)
        self.profit_history.append(1 if firm.profit > 0 else 0)

    def generate_parameters(self, stats):
        new_parameters = [0, 0, 0]
        trial_parameters = []
        for parameter in new_parameters:
            change = random.gauss(0, 0.333)
           # parameter *= (1 + change)
           # trial_parameters.append(parameter)
            trial_parameters.append(change)
        #trial_parameters.append(math.ceil(new_parameters[2] / self.efficiency_coefficient))
        trial_parameters.append(trial_parameters[2])
        #for parameter in [stats.price, stats.salary, stats.money - stats.sales, stats.sold]:
        for parameter in self.change[4:]:
        #    trial_parameters.append(0)
            trial_parameters.append(parameter)

        return new_parameters, trial_parameters


    def decide_salary(self, stats, firm):
        self.update_history(stats, firm)
        #current_data = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary, stats.money - stats.sales]
        self.decision_tree.fit(self.world_history, self.profit_history)
        #self.neural_network.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats)
            #has_profit = self.neural_network.predict(trial_parameters)
            has_profit = self.decision_tree.predict(trial_parameters)
            if has_profit == 1:
                new_parameters = (trial_parameters[0], trial_parameters[1], trial_parameters[2])
                break
        #self.price, self.salary, self.plan = [for value in new_parameters]
        firm.plan = (new_parameters[2] + 1) * firm.plan if (new_parameters[2] + 1) * firm.plan > 0 else firm.labor_productivity
        firm.price = (new_parameters[0] + 1) * firm.price if (new_parameters[0] + 1) * firm.price > 0 else 20
        firm.salary = (new_parameters[1] + 1) * firm.salary if (new_parameters[1] + 1) * firm.salary > 0 else 200
        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.current_salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
