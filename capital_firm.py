import algorithms
from service import match

from firm import Firm

class CapitalFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.id = id
        self.type = "CapitalFirm"
        for parameter in run_config:
            if parameter not in model_config or model_config[parameter]:
                setattr(self, parameter, run_config[parameter])
        decision_maker = getattr(algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)

    def produce(self):
        if hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity) / self.raw_productivity
        else:
            self.stock += len(self.workers) * self.labor_productivity
        for worker in self.workers:
            self.money -= worker.salary

