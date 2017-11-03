import math

import ace.algorithms

from .firm import Firm
from .service import match


class RawFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id, model_config, run_config, learning_method)
        self.type = "RawFirm"
        if len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")

    def produce(self):
        super().produce()
        for worker in self.workers:
            self.stock += len(self.workers) * self.labor_productivity








