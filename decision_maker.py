from abc import ABCMeta, abstractmethod

class DecisionMaker:
    __metaclass__ = ABCMeta

    def __init__(self, id):
        self.id = id

    @abstractmethod
    def decide(self, stats):
        pass

    def decide_price(self, stats):
        pass

    def decide_salary(self, stats):
        pass

