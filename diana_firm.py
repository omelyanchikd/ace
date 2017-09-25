from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random


class DianaFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.plan = firm.plan
        self.prev_price = 1000
        self.salary = firm.salary
        self.offer_count = 0
        self.type = 'DianaFirm'

    def decide_salary(self, stats, firm):
        price_increase = self.prev_price < firm.price
        already_decreased = False
        self.prev_price = firm.price
        if firm.sold >= firm.plan:
            firm.plan = firm.sold + math.floor(firm.labor_productivity)
            firm.price *= 1.05
        else:
            firm.price *= 0.95
            #if price_increase:
            #    self.price *= 0.95
            #    already_decreased = True
            #else:
            #    self.plan = self.sold if self.sold > 0 else self.efficiency_coefficient
        #self.plan = (self.plan - self.stock) // self.efficiency_coefficient * self.efficiency_coefficient
        firm.plan = firm.plan // firm.labor_productivity * firm.labor_productivity
        #self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = firm.plan // firm.labor_productivity - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        total_salary = sum([worker.salary for worker in firm.workers])
        while True:
            if self.offer_count > 0:
                firm.salary = 0.9 * (firm.price * (len(firm.workers) + self.offer_count) * firm.labor_productivity  -
                              total_salary)/self.offer_count
                if firm.salary > 0:
                    break
                firm.price *= 1.05
            else:
                break
        #print(str(self.salary) + " " + str(self.price * self.plan - total_salary - self.salary * self.offer_count))
        firm.labor_capacity = self.offer_count + len(firm.workers)
        return FirmLaborMarketAction(self.offer_count, firm.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
