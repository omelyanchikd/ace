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
        return getattr(self, 'derive_' + parameter)(control_parameters)


    def derive_salary(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if set(['price', 'plan']).issubset(control_parameters):
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return (1/(1 + 1/self.demand_elasticity) * self.plan - total_salary * self.price)/(self.price * needed_workers)
            return 0
        if set(['price', 'labor_capacity']).issubset(control_parameters):
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return (1/(1 + 1/self.demand_elasticity) * self.labor_capacity * self.labor_productivity -
                        total_salary * self.price) / (self.price * needed_workers)
            return 0
        if set(['plan', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
        elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
            needed_workers = self.labor_capacity - len(self.workers)
        elif set(['price', 'salary_budget']).issubset(control_parameters):
            needed_workers = (self.price * self.salary_budget - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers)) / \
                             (1/(1 + 1/self.demand_elasticity) * self.labor_productivity)
        else:
            return 0
        if needed_workers > 0:
            return (self.salary_budget - total_salary)/needed_workers
        return 0


    def derive_price(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if set(['salary', 'plan']).issubset(control_parameters):
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) * self.plan / (total_salary + self.salary * needed_workers)
            return 0
        if set(['salary', 'labor_capacity']).issubset(control_parameters):
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) * self.labor_capacity * self.labor_productivity / (total_salary + self.salary * needed_workers)
            return 0
        if set(['plan', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) * self.plan / self.salary_budget
            return 0
        if set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
            needed_workers = self.labor_capacity - len(self.workers)
            if needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) * self.labor_capacity * self.labor_productivity / self.salary_budget
            return 0
        if set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            if needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * (len(self.workers) + needed_workers) / self.salary_budget
            return 0
        return 0


    def derive_plan(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if set(['labor_capacity']).issubset(control_parameters):
            return math.floor(self.labor_capacity * self.labor_productivity)
        if set(['salary', 'price']).issubset(control_parameters):
            needed_workers = math.floor((total_salary * self.price - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers))/
                                         (1/(1 + 1/self.demand_elasticity) * self.labor_productivity - self.price * self.salary))
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
        elif set(['price', 'salary_budget']).issubset(control_parameters):
            needed_workers = (self.price * self.salary_budget - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers)) / \
                             (1/(1 + 1/self.demand_elasticity) * self.labor_productivity)
        else:
            return 0
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        return 0


    def derive_labor_capacity(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if set(['plan']).issubset(control_parameters):
            return math.floor(self.plan / self.labor_productivity)
        if set(['salary', 'price']).issubset(control_parameters):
            needed_workers = math.floor((total_salary * self.price - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers))/
                                         (1/(1 + 1/self.demand_elasticity) * self.labor_productivity - self.price * self.salary))
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
        elif set(['price', 'salary_budget']).issubset(control_parameters):
            needed_workers = (self.price * self.salary_budget - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers)) / \
                             (1/(1 + 1/self.demand_elasticity) * self.labor_productivity)
        else:
            return 0
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return len(self.workers) + needed_workers
        return 0


    def derive_salary_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if set(['price', 'plan']).issubset(control_parameters):
            return 1/(1 + 1/self.demand_elasticity) * self.plan / self.price
        if set(['price', 'labor_capacity']).issubset(control_parameters):
            return 1/(1 + 1/self.demand_elasticity) * self.labor_capacity * self.labor_productivity / self.price
        if set(['salary', 'plan']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
        elif set(['salary', 'labor_capacity']).issubset(control_parameters):
            needed_workers = self.labor_capacity - len(self.workers)
        elif set(['salary', 'price']).issubset(control_parameters):
            needed_workers = math.floor((total_salary * self.price - 1/(1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers)) /
                 (1/(1 + 1/self.demand_elasticity) * self.labor_productivity - self.price * self.salary))
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return total_salary + self.salary * needed_workers
        return 0




