from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class NewFirm(DecisionMaker):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.offer_count = 0
        self.price_increase_history = [0, 0, 1]
        self.plan_increase_history = [0, 0, 1]
        self.salary_increase_history  = [0, 0, 1]
        self.price_decrease_history = [0, 0, 1]
        self.plan_decrease_history = [0, 0, 1]
        self.salary_decrease_history = [0, 0, 1]
        self.price_stable_history = [0, 0, 1]
        self.plan_stable_history = [0, 0, 1]
        self.salary_stable_history = [0, 0, 1]
        self.prev_price = 20
        self.prev_salary = 200
        self.prev_plan = 50 * self.efficiency_coefficient
        self.prev_workers = 50
        self.plan = 50 * self.efficiency_coefficient
        self.type = "NewFirm"


    def decide_price(self, stats):
        return FirmGoodMarketAction(self.stock, self.price, 0)


    def decide_salary(self, stats):
        if self.prev_price < self.price:
            if self.profit >= 0:
                self.price_increase_history.append(1)
            else:
                self.price_increase_history.append(0)
        if self.prev_price > self.price:
            if self.profit >= 0:
                self.price_decrease_history.append(1)
            else:
                self.price_decrease_history.append(0)
        if self.prev_price == self.price:
            if self.profit >= 0:
                self.price_stable_history.append(1)
            else:
                self.price_stable_history.append(0)
        if self.prev_plan < self.plan:
            if self.sold >= self.plan:
                self.plan_increase_history.append(1)
            else:
                self.plan_increase_history.append(0)
        if self.prev_plan > self.plan:
            if self.sold >= self.plan:
                self.plan_decrease_history.append(1)
            else:
                self.plan_decrease_history.append(0)
        if self.prev_salary < self.salary:
            if len(self.workers) == self.prev_workers + self.offer_count:
                self.salary_increase_history.append(1)
            else:
                self.salary_increase_history.append(0)
        if self.prev_salary > self.salary:
            if len(self.workers) == self.prev_workers + self.offer_count:
                self.salary_decrease_history.append(1)
            else:
                self.salary_decrease_history.append(0)
        if self.prev_plan == self.plan:
            if self.sold >= self.plan:
                self.plan_stable_history.append(1)
            else:
                self.plan_stable_history.append(0)
        if self.prev_salary == self.salary:
            if len(self.workers) == self.prev_workers + self.offer_count:
                self.salary_stable_history.append(1)
            else:
                self.salary_stable_history.append(0)

        self.prev_price = self.price
        self.prev_plan = self.plan
        self.prev_salary = self.salary
        self.prev_workers = len(self.workers)
        price_increase_probability = numpy.mean(self.price_increase_history)
        price_decrease_probability = numpy.mean(self.price_decrease_history)
        price_stable_probability = numpy.mean(self.price_stable_history)
        salary_increase_probability = numpy.mean(self.salary_increase_history)
        salary_decrease_probability = numpy.mean(self.salary_decrease_history)
        salary_stable_probability = numpy.mean(self.salary_stable_history)
        plan_increase_probability = numpy.mean(self.plan_increase_history)
        plan_decrease_probability = numpy.mean(self.plan_decrease_history)
        plan_stable_probability = numpy.mean(self.plan_stable_history)

        total_salary = sum([worker.salary for worker in self.workers])

        max_profit = price_stable_probability * (self.price * plan_stable_probability * self.plan - total_salary -
                                          salary_stable_probability * self.salary)
        max_price = self.price
        max_plan = self.plan
        max_salary = self.salary

        expectations = []
        expected_profits = []

        for new_price in [0.95 * self.price, self.price, 1.05 * self.price]:
            for new_plan in [(self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient - self.efficiency_coefficient,
                             (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient,
                             (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient + self.efficiency_coefficient]:
                for new_salary in [0.95 * self.salary, self.salary, 1.05 * self.salary]:
                    if new_price > self.price:
                        price_probability = price_increase_probability
                    elif new_price < self.price:
                        price_probability = price_decrease_probability
                    else:
                        price_probability = price_stable_probability
                    if new_plan > self.plan:
                        plan_probability = plan_increase_probability
                    elif new_plan < self.plan:
                        plan_probability = plan_decrease_probability
                    else:
                        plan_probability = plan_stable_probability
                    if new_salary > self.salary:
                        salary_probability = salary_increase_probability
                    elif new_salary < self.salary:
                        salary_probability = salary_decrease_probability
                    else:
                        salary_probability = salary_stable_probability
                    new_profit = price_probability * (new_price * salary_probability * plan_probability * new_plan - total_salary -
                                                                                    new_salary)

                    expectations.append((new_price, new_salary, new_plan))
                    expected_profits.append(new_profit)
                   # if new_profit > max_profit:
                   #     max_price = new_price
                   #     max_salary = new_salary
                   #     max_plan = new_plan
                   #     max_profit = new_profit


        expected_profits = numpy.array(list(expected_profits - min(expected_profits)))
        self.price, self.salary, self.plan = expectations[numpy.random.choice(len(expectations), replace=False, p=expected_profits / sum(expected_profits))]
        self.plan = self.plan if self.plan > 0 else self.efficiency_coefficient

        self.offer_count = self.plan // self.efficiency_coefficient - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1

        return FirmLaborMarketAction(self.offer_count, self.salary, [])