import math

import ace.algorithms
from .service import match

from .decision_maker import DecisionMaker

from .firm import Firm

class ProductionFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.id = id
        self.type = "ProductionFirm"
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        if ('raw_budget' in self.control_parameters or 'raw_need' in self.control_parameters) and \
           ('capital_budget' in self.control_parameters or 'capital_need' in self.control_parameters) and len(self.control_parameters) < 4:
            raise AssertionError("Agent needs at least four defined control parameters to make decisions, when both raw and capital are part of the model.")
        if (('raw_budget' in self.control_parameters or 'raw_need' in self.control_parameters) or \
           ('capital_budget' in self.control_parameters or 'capital_need' in self.control_parameters)) and len(self.control_parameters) < 3:
            raise AssertionError("Agent needs at least three defined control parameters to make decisions, when either raw or capital are part of the model.")
        elif len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        self.derived_parameters = [parameter for parameter in model_config if
                                   model_config[parameter] is not None and not model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is None:
                if parameter in self.derived_parameters:
                    setattr(self, parameter, 0)
                elif parameter in self.control_parameters:
                    raise ValueError(
                        "Parameter " + parameter + " cannot be derived from others. Please define the parameter and restart the model.")
            else:
                setattr(self, parameter, run_config[parameter])
        for parameter in self.derived_parameters:
            setattr(self, parameter, self.derive(parameter, self.control_parameters))
        if hasattr(self, 'raw'):
            self.raw_expenses = 0
            self.raw_bought = 0
        if hasattr(self, 'capital'):
            self.capital_bought = 0
        decision_maker = getattr(ace.algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)

    def produce(self):
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity, self.raw * self.raw_productivity)/self.raw_productivity
            self.capital *= (1 - self.amortisation)
        elif hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity) / self.raw_productivity
        elif hasattr(self, 'capital'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.capital * self.capital_productivity)
            self.capital *= (1 - self.capital_amortization)
        else:
            self.stock += len(self.workers) * self.labor_productivity

        for worker in self.workers:
            self.money -= worker.salary









