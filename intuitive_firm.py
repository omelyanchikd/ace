from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

import random
import math
import numpy


class IntuitiveFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = firm.salary
        self.prev_workers = 50
        self.offer_count = 0
        self.period = 3
        self.history = [1000, 1000, 1000]
        self.plan = firm.plan
        self.smoothing_coefficient = 0.5
        self.type = 'Extrapolation'

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)


    def decide_salary(self, stats, firm):
        if firm.sold >= firm.plan and firm.sold > 0:
            firm.plan = 1.1 *(self.smoothing_coefficient * firm.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history))
        else:
            firm.plan = self.smoothing_coefficient * firm.sold + (1 - self.smoothing_coefficient) * numpy.mean(self.history)
        self.history.append(firm.sold)
        self.history.pop(0)
        firm.plan = firm.plan // firm.labor_productivity * firm.labor_productivity
        firm.plan = firm.plan if firm.plan > 0 else firm.labor_productivity
        if len(firm.workers) < self.prev_workers + self.offer_count:
            firm.salary *= 1.01
        else:
            firm.salary *= 0.99
        self.offer_count = firm.plan // firm.labor_productivity - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        self.prev_workers = len(firm.workers)
        total_salary = sum([worker.salary for worker in firm.workers])
        firm.price = 1.05 * (total_salary + firm.salary)/firm.plan
        firm.price = firm.price if firm.price > 0 else 0
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])