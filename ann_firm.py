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
        self.world_history = [[self.price + 1, self.salary, self.sold, len(self.workers), self.price, self.salary,
                              self.sold * 10, len(self.workers) * 10], [self.price, self.salary, self.sold, len(self.workers), self.price, self.salary,
                              self.sold * 10, len(self.workers) * 10]]
        self.profit_history = [1, 0]
        self.scaler.partial_fit(self.world_history)
        self.scaled_history = self.scaler.transform(self.world_history)
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
            change = random.gauss(0, 0.99)
            parameter *= (1 + change)
            trial_parameters.append(parameter)
        trial_parameters.append(math.floor(new_parameters[2] / self.efficiency_coefficient) - len(self.workers))
        for parameter in [stats.price, stats.salary, stats.sold, stats.unemployment_rate]:
            trial_parameters.append(parameter)
        return new_parameters, trial_parameters


    def decide_price(self, stats):
        self.update_history(stats)
        current_data = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary,
                                   stats.sold, stats.employed]
        self.scaler.partial_fit(current_data)
        self.scaled_history = self.scaler.transform(current_data)
        self.neural_network.partial_fit(self.scaled_history, numpy.array(self.profit_history))
        for i in range(0, 100):
            new_parameters, trial_parameters = self.generate_parameters(stats)
            has_profit = self.neural_network.predict(trial_parameters)
            if has_profit == 1:
                break
        self.price, self.salary, self.plan = new_parameters
        self.plan = self.plan if self.plan > 0 else 0
        self.price = self.price if self.price > 0 else 0
        self.salary = self.salary if self.salary > 0 else 0
        self.offer_count = math.floor(self.plan / self.efficiency_coefficient) - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1
        return FirmGoodMarketAction(self.stock, self.price, 0)

    def decide_salary(self, stats):
        return FirmLaborMarketAction(1, self.current_salary, [])
