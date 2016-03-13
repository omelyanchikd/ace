from abc import ABCMeta, abstractmethod


class WorldAlgorithm:
    __metaclass__ = ABCMeta

    @abstractmethod
    def apply(self, world, firm_id):
        pass
