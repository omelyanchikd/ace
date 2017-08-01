import algorithms

from firm import Firm


class RawFirm(Firm):

    def __init__(self, model_config, run_config, learning_method):
        for parameter in model_config:
            if parameter:
                setattr(self, parameter, run_config[parameter])
        decision_maker = getattr(algorithms, learning_method)
        self.decision_maker = decision_maker()



    def produce(self):
        for worker in self.workers:
            self.stock += worker.productivity * self.efficiency_coefficient
            self.money -= worker.salary
