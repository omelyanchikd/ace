from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class NewFirm(Firm):
    def __init__(self, id):
        super().__init__(id)
        self.salary = 200
        self.offer_count = 0
        self.price_increase_history = [1]
        self.plan_increase_history = [1]
        self.salary_increase_history  = [1]
        self.price_decrease_history = [1]
        self.plan_decrease_history = [1]
        self.salary_decrease_history = [1]
        self.price_stable_history = [1]
        self.plan_stable_history = [1]
        self.salary_stable_history = [1]
        self.prev_price = 20
        self.prev_salary = 200
        self.prev_plan = 50 * self.efficiency_coefficient
        self.prev_workers = 50
        self.plan = 50 * self.efficiency_coefficient


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

        max_profit = plan_stable_probability * price_stable_probability * salary_stable_probability * self.profit
        max_price = self.price
        max_plan = self.plan
        max_salary = self.salary

        for new_price in [0.95 * self.price, self.price, 1.05 * self.price]:
            for new_plan in [(self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient - self.efficiency_coefficient,
                             (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient,
                             (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient + self.efficiency_coefficient]:
                for new_salary in [0.95 * self.salary, self.salary, 1.05 * self.salary]:
                    new_profit = new_price * new_plan - total_salary - new_salary
                    if new_price > self.price:
                        new_profit *= price_increase_probability
                    elif new_price < self.price:
                        new_profit *= price_decrease_probability
                    else:
                        new_profit *= price_stable_probability
                    if new_plan > self.plan:
                        new_profit *= plan_increase_probability
                    elif new_plan < self.plan:
                        new_profit *= plan_decrease_probability
                    else:
                        new_profit *= plan_stable_probability
                    if new_salary > self.salary:
                        new_profit *= salary_increase_probability
                    elif new_salary < self.salary:
                        new_profit *= salary_decrease_probability
                    else:
                        new_profit *= salary_stable_probability
                    if new_profit > max_profit:
                        max_price = new_price
                        max_salary = new_salary
                        max_plan = new_plan
                        max_profit = new_profit
        self.price = max_price
        self.salary = max_salary
        self.plan = max_plan

        self.plan = self.plan if self.plan > 0 else self.efficiency_coefficient

        self.offer_count = self.plan // self.efficiency_coefficient - len(self.workers)
        while self.offer_count < 0:
            self.fire_worker(random.choice(list(self.workers)))
            self.offer_count += 1

        return FirmLaborMarketAction(self.offer_count, self.salary, [])