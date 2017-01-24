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

class TreeFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.type = 'TreeFirm'
        self.salary = 200
        recorded_history = pandas.read_csv("change_history.csv", sep = ";", decimal = ",")
        self.world_history = recorded_history.as_matrix(columns = ['price', 'salary', 'sold', 'workers', 'world_price', 'world_salary',
                                                                   'rest_money', 'world_sold'])
        self.world_history = self.world_history.tolist()
        self.profit_history = list(recorded_history['has_profit'])
        #self.decision_tree = tree.DecisionTreeClassifier()
        #self.decision_tree.fit(self.world_history, self.profit_history)
        #self.neural_network = Perceptron(fit_intercept=False)
        #self.neural_network.fit(self.world_history, self.profit_history)
        self.neural_network = MLPClassifier(hidden_layer_sizes=(30, ))
        self.neural_network.fit(self.world_history, self.profit_history)
        self.plan = 500
        self.offer_count = 0
        self.prev_state = [19.9, 199.9, 500, 50, 20, 200, 0, 5000]
        self.current_state = [] * 8
        self.change = [] * 8

    def update_history(self, stats):
        self.current_state = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
                              stats.money - stats.sales, stats.sold]
        self.change = [(self.current_state[i] - self.prev_state[i])/self.prev_state[i] if self.prev_state[i] != 0 else 0 for i in range(0, len(self.prev_state)) ]
        self.prev_state = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
                           stats.money - stats.sales, stats.sold]

        #self.world_history.append([self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
        #                           stats.money - stats.sales, stats.employed, stats.sold])

        self.world_history.append(self.change)
        self.profit_history.append(1 if self.profit > 0 else 0)

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


    def decide_salary(self, stats):
        self.update_history(stats)
        #current_data = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary, stats.money - stats.sales]
        #self.decision_tree.fit(self.world_history, self.profit_history)
        self.neural_network.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats)
            has_profit = self.neural_network.predict(trial_parameters)
            #has_profit = self.decision_tree.predict(trial_parameters)
            if has_profit == 1:
                new_parameters = (trial_parameters[0], trial_parameters[1], trial_parameters[2])
                break
        #self.price, self.salary, self.plan = [for value in new_parameters]
        self.plan = (new_parameters[2] + 1) * self.plan if (new_parameters[2] + 1) * self.plan > 0 else self.efficiency_coefficient
        self.price = (new_parameters[0] + 1) * self.price if (new_parameters[0] + 1) * self.price > 0 else 20
        self.salary = (new_parameters[1] + 1) * self.salary if (new_parameters[1] + 1) * self.salary > 0 else 200
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.current_salary, [])

    def decide_price(self, stats):
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmGoodMarketAction(self.stock, self.price, 0)
