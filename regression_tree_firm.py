from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction

from sklearn.tree import DecisionTreeRegressor

import numpy
import random
import math
import pandas

def change(new_value, old_value):
    if isinstance(new_value, set):
        return (len(new_value) - len(old_value))/len(old_value) if len(old_value) != 0 else 0
    return (new_value - old_value)/old_value if old_value != 0 else 0

def generate_sample_data(sample_size):
    return [random.uniform(-1, 1) for i in range(sample_size + 1)]


class RegressionTreeFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        self.external = ['price', 'sales', 'workers', 'sold', 'profit', 'world_unemployment_rate', 'world_salary', 'world_sales', 'world_sold']
        if hasattr(firm, 'raw'):
            self.external.append('raw')
        if hasattr(firm, 'capital'):
            self.external.append('capital')

        for parameter in self.external:
            if parameter == 'workers':
                setattr(self, 'previous_workers', len(firm.workers))
            elif hasattr(firm, parameter):
                setattr(self, 'previous_' + parameter, getattr(firm, parameter))
            else:
                setattr(self, 'previous_' + parameter, 0)

        for parameter in firm.control_parameters:
           # setattr(self, 'sample_' + parameter, self.history[[parameter]])
            setattr(self, 'regression_' + parameter, learning_data['regression_' + parameter])
            #setattr(self, 'prediction_interval_' + parameter, learning_data['prediction_interval_' + parameter])

        for parameter in ['world_unemployment_rate', 'world_salary', 'world_sales', 'world_sold']:
            setattr(self, 'regression_' + parameter, learning_data['regression_' + parameter])


        self.change = [0] * len(self.external)
        #self.state = {parameter: getattr(firm, parameter) for parameter in self.external}

        self.type = "RegressionTreeFirm"

    def decide_salary(self, stats, firm):
        #self.update_state(firm)
        prediction_state = []
        current_state = []
        for parameter in self.external:
            if parameter == 'workers':
                current_state.append(len(firm.workers))
            elif hasattr(firm, parameter):
                current_state.append(getattr(firm, parameter))
            else:
                current_state.append(getattr(stats, parameter.replace('world_','')))
       #     if parameter == 'workers':
        #        change = (len(firm.workers) - getattr(self, 'previous_' + parameter))/getattr(self, 'previous_' + parameter) \
        #            if getattr(self, 'previous_' + parameter) != 0 else 0
        #        current_state.append(change)
        #        prediction_state.append(change)
        #        setattr(self, 'previous_' + parameter, len(firm.workers))
        #    elif hasattr(firm, parameter):
        #        current_state.append((getattr(firm, parameter) - getattr(self, 'previous_' + parameter))/getattr(self, 'previous_' + parameter)
        #                             if getattr(self, 'previous_' + parameter) != 0 else 0)
        #        prediction_state.append((getattr(firm, parameter) - getattr(self, 'previous_' + parameter)) / getattr(self,
        #                                                                                                           'previous_' + parameter)
        #                             if getattr(self, 'previous_' + parameter) != 0 else 0)
        #        setattr(self, 'previous_' + parameter, getattr(firm, parameter))
      #      else:
      #          current_state.append(getattr(self, 'regression_' + parameter).predict(numpy.array(prediction_state).reshape(1,-1))[0])
      #          current_state.append((getattr(stats, parameter.replace('world_', '')) - getattr(self, 'previous_' + parameter)) / getattr(self,
#                                                                                                                   'previous_' + parameter)
       #                              if getattr(self, 'previous_' + parameter) != 0 else 0)
       #         setattr(self, 'previous_' + parameter, getattr(stats, parameter.replace('world_', '')))

        for parameter in firm.control_parameters:
            value = getattr(firm, parameter)
            if parameter in ['plan', 'labor_capacity', 'raw_need', 'capital_need']:
            #    firm.__setattr__(parameter, math.ceil(self.get_parameter(parameter, current_state)))
                firm.__setattr__(parameter, math.ceil(getattr(self, 'regression_' + parameter).predict(numpy.array(current_state).reshape(1, -1))[0]))
            #    firm.__setattr__(parameter, math.ceil(getattr(firm, parameter) * (1 + getattr(self, 'regression_' + parameter).predict(numpy.array(current_state).reshape(1, -1))[0])))

            else:
                #firm.__setattr__(parameter, self.get_parameter(parameter, current_state))
                firm.__setattr__(parameter, getattr(self, 'regression_' + parameter).predict(numpy.array(current_state).reshape(1, -1))[0])
            #    firm.__setattr__(parameter, getattr(firm, parameter) * (1 + getattr(self, 'regression_' + parameter).predict(numpy.array(current_state).reshape(1, -1))[0]))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)


    def update_state(self, firm):
        self.change = [change(getattr(firm, parameter), self.state[parameter]) for parameter in self.external]
        self.state = {parameter:getattr(firm, parameter) for parameter in self.external}


