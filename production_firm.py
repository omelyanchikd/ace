import math

import ace.algorithms
from .service import match

from .decision_maker import DecisionMaker

from .firm import Firm

class ProductionFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method, learning_data):
        super().__init__(id, model_config, run_config, learning_method, learning_data)
        self.type = "ProductionFirm"
        if ('raw_budget' in self.control_parameters or 'raw_need' in self.control_parameters) and \
           ('capital_budget' in self.control_parameters or 'capital_need' in self.control_parameters) and len(self.control_parameters) < 4:
            raise AssertionError("Agent needs at least four defined control parameters to make decisions, when both raw and capital are part of the model.")
        if (('raw_budget' in self.control_parameters or 'raw_need' in self.control_parameters) or \
           ('capital_budget' in self.control_parameters or 'capital_need' in self.control_parameters)) and len(self.control_parameters) < 3:
            raise AssertionError("Agent needs at least three defined control parameters to make decisions, when either raw or capital are part of the model.")
        elif len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        if hasattr(self, 'raw'):
            self.raw_expenses = 0
            self.raw_bought = 0
        if hasattr(self, 'capital'):
            self.capital_bought = 0
            self.capital_expenses = 0

    def produce(self):
        super().produce()
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity, self.raw * self.raw_productivity)/self.raw_productivity
            self.capital *= (1 - self.capital_amortization)
        elif hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity) / self.raw_productivity
        elif hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity)
            self.capital *= (1 - self.capital_amortization)
        else:
            self.stock += len(self.workers) * self.labor_productivity










