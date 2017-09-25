from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

from sklearn.linear_model import Perceptron
from sklearn.preprocessing import StandardScaler

from sklearn import tree

import numpy
import random
import math

class AnnFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = firm.salary
        #self.scaler = StandardScaler()
        self.neural_network = Perceptron(fit_intercept=False)
        #self.decision_tree = tree.DecisionTreeClassifier()
        #self.world_history = [[self.price + 1, self.salary, self.sold, len(self.workers), self.price, self.salary,
        #                      self.sold * 10, len(self.workers) * 10], [self.price, self.salary, self.sold, len(self.workers), self.price, self.salary,
        #                      self.sold * 10, len(self.workers) * 10]]
        self.world_history = [[15, 200, 10, 20, 200],
                              [25, 200, 10, 20, 200],
                              [20, 195, 2000, 21, 190],
                              [25, 200, 1000, 15, 150],
                              [20, 195, 90, 21, 205],
                              [300, 250, 10, 20, 200]]
        self.profit_history = [0, 1, 1, 0, 0, 1]
        #self.scaler.fit(self.world_history)
        #self.scaled_history = self.scaler.fit_transform(self.world_history)
        self.neural_network.fit(numpy.array(self.world_history), numpy.array(self.profit_history))
        #self.decision_tree.fit(self.world_history, self.profit_history)
        self.plan = firm.plan
        self.offer_count = 0
        self.type = "AnnFirm"

    def update_history(self, stats, firm):
        self.world_history.append([firm.price, firm.salary, firm.sold, stats.price, stats.salary])
        self.profit_history.append(1 if firm.profit > 0 else 0)

    def generate_parameters(self, stats, firm):
        new_parameters = [firm.price, firm.salary, firm.sold]
        trial_parameters = []
        for parameter in new_parameters:
            change = random.gauss(0, 1)
            parameter *= (1 + change)
            trial_parameters.append(parameter)
        #trial_parameters.append(math.ceil(new_parameters[2] / self.efficiency_coefficient))
        for parameter in [stats.price, stats.salary]:
            trial_parameters.append(parameter)
        return new_parameters, trial_parameters


    def decide_salary(self, stats, firm):
        self.update_history(stats, firm)
        current_data = [firm.price, firm.salary, firm.sold, stats.price, stats.salary]
        #self.scaler.partial_fit(current_data)
        #self.scaled_history = self.scaler.fit_transform(self.world_history)
        #self.neural_network.partial_fit(self.scaled_history, [firm.profit])
        self.neural_network.fit(self.world_history, self.profit_history)
        #self.decision_tree.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats, firm)
            has_profit = self.neural_network.predict(trial_parameters)
            #has_profit = self.decision_tree.predict(trial_parameters)
            if has_profit == 1:
                new_parameters = (trial_parameters[0], trial_parameters[1], trial_parameters[2])
                break
        firm.price, firm.salary, firm.plan = new_parameters
        firm.plan = new_parameters[2]if new_parameters[2] > 0 else firm.labor_productivity
        firm.price = new_parameters[0] if new_parameters[0] > 0 else 20
        firm.salary = new_parameters[1] if new_parameters[1] > 0 else 200
        self.offer_count = math.floor(firm.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
