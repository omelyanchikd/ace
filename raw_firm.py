import math

import ace.algorithms

from .firm import Firm
from .service import match


class RawFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.type = "RawFirm"
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        if len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        self.derived_parameters = [parameter for parameter in model_config if not model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is None:
                if parameter in self.derived_parameters:
                    setattr(self, parameter, 0)
                elif parameter in self.control_parameters:
                    raise ValueError("Parameter " + parameter + " cannot be derived from others. Please define the parameter and restart the model.")
            else:
                setattr(self, parameter, run_config[parameter])
        for parameter in self.derived_parameters:
            setattr(self, parameter, self.derive(parameter, self.control_parameters))
        decision_maker = getattr(ace.algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)

    def produce(self):
        for worker in self.workers:
            self.stock += len(self.workers) * self.labor_productivity
            self.money -= worker.salary







