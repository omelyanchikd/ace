from algorithm import Algorithm
from firm_action import FirmAction


class BaseAlgorithm(Algorithm):
    def decide(self, firm):
        return FirmAction(0, 0, 0, 0, 0, 0, [])
