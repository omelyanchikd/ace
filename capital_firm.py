import math

import ace.algorithms
from .service import match

from .firm import Firm

class CapitalFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id, model_config, run_config, learning_method)
        self.type = "CapitalFirm"
        if ('raw_budget' in self.control_parameters or 'raw_need' in self.control_parameters) and len(self.control_parameters) < 3:
            raise AssertionError("Agent needs at least three defined control parameters to make decisions, when raw is part of the model.")
        elif len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        if hasattr(self, 'raw'):
            self.raw_expenses = 0
            self.raw_bought = 0

    def produce(self):
        super().produce()
        if hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity) / self.raw_productivity
        else:
            self.stock += len(self.workers) * self.labor_productivity



