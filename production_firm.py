import algorithms
from decision_maker import DecisionMaker

from firm import Firm

class ProductionFirm(Firm):

    def __init__(self, model_config, run_config, learning_method):
        for parameter in model_config:
            if parameter:
                setattr(self, parameter, run_config[parameter])
        decision_maker = getattr(algorithms, learning_method)
        self.decision_maker = decision_maker()

    def produce(self):
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_efficiency, self.capital * self.capital_efficiency, self.raw * self.raw_efficiency)
            self.raw -= min(len(self.workers) * self.labor_efficiency, self.capital * self.capital_efficiency, self.raw * self.raw_efficiency)/self.raw_efficiency
            self.capital *= (1 - self.amortisation)
        elif hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_efficiency, self.raw * self.raw_efficiency)
            self.raw -= min(len(self.workers) * self.labor_efficiency, self.raw * self.raw_efficiency) / self.raw_efficiency
        elif hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_efficiency, self.capital * self.capital_efficiency)
            self.capital *= (1 - self.amortisation)
        for worker in self.workers:
            self.money -= worker.salary
