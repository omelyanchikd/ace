from decision_maker import DecisionMaker
from firm import Firm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction

import random

class RandomFirm(DecisionMaker):
    def __init__(self, id, firm):
        super().__init__(id, firm)
        self.salary = 200
        self.type = 'RandomFirm'
   #     ['price', 'salary', 'sold', 'workers', 'world_price', 'world_salary',
   #      'rest_money', 'world_employed', 'world_sold']
    #    self.prev_state = [20, 200, 500, 50, 20, 200, 0, 500, 5000]
    #    self.current_state = [20, 200, 500, 50, 20, 200, 0, 500, 5000]
    #    self.change = [(self.current_state[i] - self.prev_state[i])/self.prev_state[i] if self.prev_state[i] != 0 else self.current_state[i] for i in range(0, len(self.prev_state)) ]


    def decide_price(self, stats, firm):
        self.price = random.uniform(10, 30)
        return FirmGoodMarketAction(firm.stock, self.price, 0)

    def decide_salary(self, stats, firm):
        self.salary = random.uniform(150, 250)
     #   self.current_state = [self.price, self.salary, self.sold, len(self.workers), stats.price, stats.salary, stats.money - ]

        self.labor_capacity = len(firm.workers) + 1
        return FirmLaborMarketAction(1, self.salary, [])
