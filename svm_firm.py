from .decision_maker import DecisionMaker
from .firm import Firm
from .firm_action import FirmAction
from .firm_goodmarket_action import FirmGoodMarketAction
from .firm_labormarket_action import FirmLaborMarketAction


import numpy
import random
import math

class SvmFirm(DecisionMaker):
    def __init__(self, id, firm, learning_data):
        super().__init__(id)
        #self.scaler = StandardScaler()
        self.svm = learning_data['svm']
        for parameter in ['world_salary', 'world_price', 'world_sold', 'world_sales']:
            setattr(self, 'svm_' + parameter, learning_data['svm_' + parameter])
        self.external = ['salary', 'plan', 'price', 'world_salary', 'world_price', 'world_sold', 'world_sales']
        self.type = "SvmFirm"
        for parameter in self.external:
            if parameter == 'workers':
                setattr(self, 'previous_workers', len(firm.workers))
            elif hasattr(firm, parameter):
                setattr(self, 'previous_' + parameter, getattr(firm, parameter))
            else:
                setattr(self, 'previous_' + parameter, 0)

    def update_history(self, stats, firm, type):
        self.world_history.append(firm.control_parameters + [getattr(stats, type + '_price'), getattr(stats, type + '_salary')])
        self.profit_history.append(1 if firm.profit > 0 else 0)

    def generate_parameters(self, firm):
        old_parameters = {parameter:getattr(firm, parameter) for parameter in firm.control_parameters + ['price']}
        trial_parameters = []
        for parameter in self.external[:2]:
            change = random.gauss(0, 0.1)
            #parameter *= (1 + change)
            trial_parameters.append(change)
            if parameter == 'plan':
                setattr(firm, parameter, math.ceil((1 + change) * getattr(firm,parameter)))
                trial_parameters[1] = (firm.plan - old_parameters['plan'])/old_parameters['plan'] if old_parameters['plan'] > 0 else 0
            else:
                setattr(firm, parameter, (1 + change) * getattr(firm, parameter))
        firm.price = firm.derive_price(firm.control_parameters)
        trial_parameters.append((firm.price - old_parameters['price'])/old_parameters['price'] if old_parameters['price'] > 0 else 0)
        for parameter in self.external[3:]:
            trial_parameters.append(getattr(self, 'svm_' + parameter).predict(numpy.array(trial_parameters[:3]).reshape(1, -1)))
        for parameter in old_parameters:
            setattr(firm, parameter, old_parameters[parameter])
        return trial_parameters


    def decide_salary(self, stats, firm):
        current_state = []
        for parameter in self.external:
            #if parameter == 'workers':
            #    current_state.append(len(firm.workers))
            #elif hasattr(firm, parameter):
            #    current_state.append(getattr(firm, parameter))
            #else:
            #    current_state.append(getattr(stats, parameter.replace('world_', '')))
                 if parameter == 'workers':
                    change = (len(firm.workers) - getattr(self, 'previous_' + parameter))/getattr(self, 'previous_' + parameter) \
                        if getattr(self, 'previous_' + parameter) != 0 else 0
                    current_state.append(change)
                    setattr(self, 'previous_' + parameter, len(firm.workers))
                 elif hasattr(firm, parameter):
                    current_state.append((getattr(firm, parameter) - getattr(self, 'previous_' + parameter))/getattr(self, 'previous_' + parameter)
                                         if getattr(self, 'previous_' + parameter) != 0 else 0)
                    setattr(self, 'previous_' + parameter, getattr(firm, parameter))
                 else:
                    current_state.append((getattr(stats, parameter.replace('world_', '')) - getattr(self, 'previous_' + parameter)) / getattr(self,
                                                                                                                       'previous_' + parameter)
                                         if getattr(self, 'previous_' + parameter) != 0 else 0)
                    setattr(self, 'previous_' + parameter, getattr(stats, parameter.replace('world_', '')))
        #type = firm.type[:len(firm.type) - 4].lower()
        new_parameters = current_state[:2]
        for i in range(0, 100):
            trial_parameters = self.generate_parameters(firm)
            has_profit = self.svm.predict(numpy.array(trial_parameters).reshape(1, -1))
            if has_profit == 1:
                new_parameters = trial_parameters[:len(firm.control_parameters)]
                break
        for i, parameter in enumerate(firm.control_parameters):
            setattr(firm, parameter, getattr(firm, parameter) * (1 + new_parameters[i]))


    def decide_price(self, stats, firm):
        return FirmGoodMarketAction(firm.stock, firm.price, 0)
