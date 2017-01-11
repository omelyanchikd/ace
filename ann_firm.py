from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

from sklearn.linear_model import Perceptron
from sklearn.preprocessing import StandardScaler

import numpy
import random
import math

class AnnFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.scaler = StandardScaler()
        self.neural_network = Perceptron()
        #self.world_history = [[self.price + 1, self.salary, self.sold, len(self.workers), self.price, self.salary,
        #                      self.sold * 10, len(self.workers) * 10], [self.price, self.salary, self.sold, len(self.workers), self.price, self.salary,
        #                      self.sold * 10, len(self.workers) * 10]]
        self.world_history = [[15, 200, 10, 1, 20, 200, 2000, 200],
                              [25, 200, 10, 1, 20, 200, 1500, 200],
                              [20, 195, 2000, 200, 21, 190, 3000, 300],
                              [25, 200, 1000, 200, 15, 150, 3000, 500],
                              [20, 195, 90, 10, 21, 205, 2000, 300],
                              [300, 250, 10, 1, 20, 200, 2000, 200]]
        self.profit_history = [0, 1, 1, 0, 0, 1]
        #self.scaler.fit(self.world_history)
        self.scaled_history = self.scaler.fit_transform(self.world_history)
        self.neural_network.fit(numpy.array(self.world_history), numpy.array(self.profit_history))
        self.plan = 0
        self.offer_count = 0

    def update_history(self, stats):
        self.world_history.append([self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
                                   stats.sold, stats.employed])
        self.profit_history.append(1 if self.profit > 0 else 0)

    def generate_parameters(self, stats):
        new_parameters = [self.price, self.salary, self.sold]
        trial_parameters = []
        for parameter in new_parameters:
            change = random.gauss(0, 0.33)
            parameter *= (1 + change)
            trial_parameters.append(parameter)
        trial_parameters.append(math.floor(new_parameters[2] / self.efficiency_coefficient))
        for parameter in [stats.price, stats.salary, stats.sold, stats.employed]:
            trial_parameters.append(parameter)
        return new_parameters, trial_parameters


    def decide_salary(self, stats):
        self.update_history(stats)
        current_data = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
                                   stats.sold, stats.employed]
        self.scaler.partial_fit(current_data)
#        self.scaled_history = self.scaler.transform(self.world_history)
#        self.neural_network.partial_fit(self.scaled_history, [self.profit])
        self.neural_network.fit(self.world_history, self.profit_history)
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats)
            has_profit = self.neural_network.predict(trial_parameters)
            if has_profit == 1:
                new_parameters = (trial_parameters[0], trial_parameters[1], trial_parameters[2])
                break
        self.price, self.salary, self.plan = new_parameters
        self.plan = new_parameters[2] if new_parameters[2] > 0 else self.efficiency_coefficient
        self.price = new_parameters[0] if new_parameters[0] > 0 else self.price
        self.salary = new_parameters[1] if new_parameters[1] > 0 else self.salary
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.current_salary, [])

    def decide_price(self, stats):
        self.labor_capacity = len(self.workers) + self.offer_count
        return FirmGoodMarketAction(self.stock, self.price, 0)
