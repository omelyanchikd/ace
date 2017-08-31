import algorithms

from firm import Firm
from service import match



class RawFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.id = id
        self.type = "RawFirm"
        for parameter in run_config:
            if parameter not in model_config or model_config[parameter]:
                setattr(self, parameter, run_config[parameter])
        decision_maker = getattr(algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)




    def produce(self):
        for worker in self.workers:
            self.stock += len(self.workers) * self.labor_productivity
            self.money -= worker.salary
