from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_labormarket_action import FirmLaborMarketAction
from firm_goodmarket_action import FirmGoodMarketAction

import math
import random
import numpy

def argmax(two_dimensional_list, dimension):
    #    arg_max = 0
    #    max_val = two_dimensional_list[dimension][0]
    #    for i in range(0,len(two_dimensional_list[dimension])):
    #        if two_dimensional_list[dimension][i] > max_val:
    #            max_val = two_dimensional_list[dimension][i]
    #            arg_max = i
    qs = numpy.array([q - min(two_dimensional_list[dimension]) for q in two_dimensional_list[dimension]])
    indexes = [i for i in range(len(two_dimensional_list[dimension]))]
    arg_max = numpy.random.choice(indexes, replace = False, p = qs/sum(qs))
    return arg_max

class QlearningFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        #self.plan = 50 * self.labor_productivity
        #self.salary = 200
        #self.offer_count = 0
        self.prev_workers = 50
        self.actions = [(0.01, firm.labor_productivity), (0.01, 0), (0.01, -firm.labor_productivity),
                        (0, firm.labor_productivity), (0, 0), (0, -firm.labor_productivity),
                        (-0.01, firm.labor_productivity), (-0.01, 0), (-0.01, -firm.labor_productivity)]
        self.action = (0,0)
        self.state = 0
        self.alpha = 0.5
        self.gamma = 0.5
        self.q = []
        for state in range(0, 6):
            self.q.append([])
            for action in range(0, 9):
                self.q[state].append(100)
        self.type = "QlearningFirm"
        self.price = firm.price
        self.salary = firm.salary
        self.workers = len(firm.workers)
        self.offer_count = 0

    def decide(self, stats, firm):
        return FirmAction(0, 0, 0, 0, 0, 0, [])

    def decide_salary(self, stats, firm):
        self.update_state(firm)
        self.prev_workers = len(firm.workers)
        self.update(firm)
        self.action = self.actions[argmax(self.q, self.state)]
        self.price = firm.price * (1 + self.action[0])
        self.price = self.price if self.price > 0 else 0
        self.plan = firm.plan + self.action[1]
        self.plan = (self.plan - firm.stock) // firm.labor_productivity * firm.labor_productivity
        self.plan = self.plan if self.plan >= 0 else 0
        self.offer_count = math.floor(self.plan / firm.labor_productivity) - len(firm.workers)
        while self.offer_count < 0:
            firm.fire_worker(random.choice(list(firm.workers)))
            self.offer_count += 1
        total_salary = sum([worker.salary for worker in firm.workers])
        while True:
            if self.offer_count > 0:
                self.salary = 0.95 * (
                self.price * (len(firm.workers) + self.offer_count) * firm.labor_productivity -
                total_salary) / self.offer_count
                if self.salary > 0:
                    break
                self.price *= 1.05
            else:
                break
        firm.labor_capacity = len(firm.workers) + self.offer_count
        return FirmLaborMarketAction(self.offer_count, self.salary, [])

    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, self.price, 0)

    def update_state(self, firm):
        if len(firm.workers) == 0:
            self.state = 5
        elif firm.sold == 0:
            self.state = 4
        elif firm.sold >= firm.plan and len(firm.workers) == self.prev_workers + self.offer_count:
            self.state = 0
        elif firm.sold < firm.plan and len(firm.workers) == self.prev_workers + self.offer_count:
            self.state = 1
        elif firm.sold == firm.plan and len(firm.workers) < self.prev_workers + self.offer_count:
            self.state = 2
        else:
            self.state = 3

    def update(self, firm):
        current_action = self.actions.index(self.action)
        self.q[self.state][current_action] = self.q[self.state][current_action] + self.alpha * (firm.profit + self.gamma * max(self.q[self.state]) - self.q[self.state][current_action])


