from firm import Firm
from abc import ABCMeta, abstractmethod


class Algorithm:
    __metaclass__ = ABCMeta

    @abstractmethod
    def decide(self, firm):
        pass
