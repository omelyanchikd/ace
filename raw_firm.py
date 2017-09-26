import math

import algorithms

from firm import Firm
from service import match


class RawFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.id = id
        self.type = "RawFirm"
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        if len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        self.derived_parameters = [parameter for parameter in model_config if not model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is None:
                if parameter in self.derived_parameters:
                    setattr(self, parameter, 0)
                else:
                    raise ValueError("Parameter " + parameter + " cannot be derived from others. Please define the parameter and restart the model.")
            else:
                setattr(self, parameter, run_config[parameter])
        for parameter in self.derived_parameters:
            setattr(self, parameter, self.derive(parameter, self.control_parameters))
        decision_maker = getattr(algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)

    def produce(self):
        for worker in self.workers:
            self.stock += len(self.workers) * self.labor_productivity
            self.money -= worker.salary


    def derive(self, parameter, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if len(set(control_parameters) ^ set(['salary', 'price'])) == 0:
            needed_workers = math.floor((total_salary * self.price - 1.05 * self.labor_productivity * len(self.workers)/
                                         (1.05 * self.labor_productivity - self.price * self.salary)))
            if needed_workers >= 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'plan':
                    return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
                if parameter == 'labor_capacity':
                    return len(self.workers) + needed_workers
                if parameter == 'salary_budget':
                    return total_salary + self.salary * needed_workers
            return 0
        if len(set(control_parameters) ^ set(['salary', 'plan'])) == 0:
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers >= 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'price':
                    return 1.05 * self.plan / (total_salary + self.salary * needed_workers)
                if parameter == 'labor_capacity':
                    return len(self.workers) + needed_workers
                if parameter == 'salary_budget':
                    return total_salary + self.salary * needed_workers
            return 0
        if len(set(control_parameters) ^ set(['price', 'plan'])) == 0:
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'salary':
                    return (1.05 * self.plan - total_salary * self.price)/(self.price * needed_workers)
                if parameter == 'labor_capacity':
                    return len(self.workers) + needed_workers
                if parameter == 'salary_budget':
                    return 1.05 * self.plan / self.price
            return 0
        if len(set(control_parameters) ^ set(['salary', 'labor_capacity'])) == 0:
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers >= 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'price':
                    return 1.05 * self.labor_productivity * self.labor_capacity / (total_salary + self.salary * needed_workers)
                if parameter == 'plan':
                    return self.labor_productivity * self.labor_capacity
                if parameter == 'salary_budget':
                    return total_salary + self.salary * needed_workers
            return 0
        if len(set(control_parameters) ^ set(['price', 'labor_capacity'])) == 0:
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'salary':
                    return (1.05 * self.labor_productivity * self.labor_capacity - total_salary * self.price)/(self.price * needed_workers)
                if parameter == 'plan':
                    return self.labor_productivity * self.labor_capacity
                if parameter == 'salary_budget':
                    return 1.05 * self.labor_productivity * self.labor_capacity / self.price
            return 0
        if len(set(control_parameters) ^ set(['salary', 'salary_budget'])) == 0:
            needed_workers = math.floor((self.salary_budget - total_salary)/self.salary)
            if needed_workers >= 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'price':
                    return 1.05 * self.labor_productivity * (len(self.workers) + needed_workers) / self.salary_budget
                if parameter == 'plan':
                    return (len(self.workers) + needed_workers) * self.labor_productivity
                if parameter == 'labor_capacity':
                    return len(self.workers) + needed_workers
            return 0
        if len(set(control_parameters) ^ set(['price', 'salary_budget'])) == 0:
            needed_workers = (self.price * self.salary_budget - 1.05 * self.labor_productivity * len(self.workers)) / (1.05 * self.labor_productivity)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'salary':
                    return (self.salary_budget - total_salary) / needed_workers
                if parameter == 'plan':
                    return self.price * self.salary_budget/1.05
                if parameter == 'labor_capacity':
                    return self.price * self.salary_budget/(1.05 * self.labor_productivity)
            return 0
        if len(set(control_parameters) ^ set(['plan', 'labor_capacity'])) == 0:
            raise ValueError('Plan and labor capacity are not enough to derive all other control parameters')
            return 0
        if len(set(control_parameters) ^ set(['plan', 'salary_budget'])) == 0:
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'salary':
                    return (self.salary_budget - total_salary) / needed_workers
                if parameter == 'price':
                    return self.salary_budget/(1.05 * self.plan)
                if parameter == 'labor_capacity':
                    return len(self.workers) + needed_workers
            return 0
        if len(set(control_parameters) ^ set(['labor_capacity', 'salary_budget'])) == 0:
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                if parameter == 'salary':
                    return (self.salary_budget - total_salary) / needed_workers
                if parameter == 'price':
                    return self.salary_budget/(1.05 * self.labor_capacity * self.labor_productivity)
                if parameter == 'plan':
                    return self.labor_capacity * self.labor_productivity
            return 0
        return 0

