import math

import algorithms
from service import match

from firm import Firm

class CapitalFirm(Firm):

    def __init__(self, id, model_config, run_config, learning_method):
        super().__init__(id)
        self.id = id
        self.type = "CapitalFirm"
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        if len(self.control_parameters) < 2:
            raise AssertionError("Agent needs at least two defined control parameters to make decisions.")
        self.derived_parameters = [parameter for parameter in model_config if model_config[parameter] is not None and not model_config[parameter]]
        for parameter in run_config:
            if run_config[parameter] is None:
                if parameter in self.derived_parameters:
                    setattr(self, parameter, 0)
                elif model_config[parameter] is not None:
                    raise ValueError("Parameter " + parameter + " cannot be derived from others. Please define the parameter and restart the model.")
            else:
                setattr(self, parameter, run_config[parameter])
        for parameter in self.derived_parameters:
            setattr(self, parameter, self.derive(parameter, self.control_parameters))
        decision_maker = getattr(algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)

    def produce(self):
        if hasattr(self, 'raw'):
            self.stock += min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity)
            self.raw -= min(len(self.workers) * self.labor_productivity, self.raw * self.raw_productivity) / self.raw_productivity
        else:
            self.stock += len(self.workers) * self.labor_productivity
        for worker in self.workers:
            self.money -= worker.salary


    def derive_salary(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if hasattr(self, 'raw'):
            if set(['price', 'plan', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.plan  * (1 + 1 / self.demand_elasticity) - total_salary -
                            self.raw_budget)/needed_workers
                return 0
            if set(['price', 'labor_capacity', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.labor_capacity * self.labor_productivity  * (1 + 1 / self.demand_elasticity) -
                            total_salary - self.raw_budget)/needed_workers
                return 0
            if set(['price', 'raw_need', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.raw_need * self.raw_productivity  * (1 + 1 / self.demand_elasticity) -
                            total_salary - self.raw_budget)/needed_workers
                return 0
            if set(['plan', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['raw_need', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
            elif set(['price', 'raw_budget', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget + self.raw_budget)/((1 + 1/self.demand_elasticity) *
                                                        self.price * self.labor_productivity))
            else:
                return 0
            if needed_workers > 0:
                return (self.salary_budget - total_salary) / needed_workers
            return 0
        return super().derive_salary(control_parameters)


    def derive_price(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if hasattr(self, 'raw'):
            if set(['salary', 'plan', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1/(1 + 1/self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget)/ \
                           self.plan
                return 0
            if set(['salary', 'labor_capacity', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1/(1 + 1/self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget)/ \
                           (self.labor_capacity * self.labor_productivity)
                return 0
            if set(['salary', 'raw_need', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_productivity * self.raw_need / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget) / \
                           (self.raw_need * self.raw_productivity)
                return 0
            if set(['plan', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget) / self.plan
            if set(['labor_capacity', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget) / \
                       (self.labor_capacity * self.labor_productivity)
            if set(['raw_need', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget) / \
                       (self.raw_need * self.raw_productivity)
            if set(['salary', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget) / \
                           ((len(self.workers) + needed_workers) * self.labor_productivity)
                return 0
        return super().derive_price(control_parameters)


    def derive_plan(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw'):
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity)
            if set(['raw_need']).issubset(control_parameters):
                return math.floor(self.raw_need * self.raw_productivity)
            if set(['salary', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.raw_budget) -
                self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers) -
                    1/(1 + 1/self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget) -
                   self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        return super().derive_plan(control_parameters)


    def derive_labor_capacity(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan/ self.labor_productivity)
            if set(['raw_need']).issubset(control_parameters):
                return math.floor(self.raw_need * self.raw_productivity / self.labor_productivity)
            if set(['salary', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.raw_budget) -
                self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers) -
                    1/(1 + 1/self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget) -
                   self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(len(self.workers) + needed_workers)
        return super().derive_labor_capacoty(control_parameters)


    def derive_raw_need(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if set(['plan']).issubset(control_parameters):
            return math.floor(self.plan / self.raw_productivity)
        if set(['labor_capacity']).issubset(control_parameters):
            return math.floor(self.labor_capacity * self.labor_productivity / self.raw_productivity)
        if set(['salary', 'price', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor((1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.raw_budget) -
                                         self.labor_productivity * self.price * len(self.workers)) / (
                                        self.labor_productivity * len(self.workers) -
                                        1 / (1 + 1 / self.demand_elasticity) * self.salary))
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
        elif set(['price', 'salary_budget', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor((1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget) -
                                         self.labor_productivity * self.price * len(self.workers)) / (
                                        self.labor_productivity * len(self.workers)))
        else:
            return 0
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return math.floor((len(self.workers) + needed_workers) * self.labor_productivity / self.raw_productivity)
        return 0


    def derive_salary_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw'):
            if set(['price', 'plan', 'raw_budget']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.raw_budget
            if set(['price', 'labor_capacity', 'raw_budget']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.raw_budget
            if set(['price', 'raw_need', 'raw_budget']).issubset(control_parameters):
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.raw_budget
            if set(['salary', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['salary', 'raw_need']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1/(1 + self.demand_elasticity) * (total_salary + self.raw_budget) - self.labor_productivity *
                     self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                        1/(1 + 1/self.demand_elasticity) * self.salary))
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return total_salary + self.salary * needed_workers
            return 0
        return super().derive_salary_budget(control_parameters)


    def derive_raw_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if set(['price', 'plan', 'salary_budget']).issubset(control_parameters):
            return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget
        if set(['price', 'labor_capacity', 'salary_budget']).issubset(control_parameters):
            return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget
        if set(['price', 'raw_need', 'salary_budget']).issubset(control_parameters):
            return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget
        if set(['salary', 'plan', 'price']).issubset(control_parameters):
            needed_workers = math.floor(self.plan/self.labor_productivity) - len(self.workers)
            return self.price * self.plan * (1 + 1 / self.demand_elasticity) - total_salary - self.salary * needed_workers
        if set(['salary', 'labor_capacity', 'price']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
            return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                   total_salary - self.salary * needed_workers
        if set(['salary', 'raw_need', 'price']).issubset(control_parameters):
            needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
            return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                   total_salary - self.salary * needed_workers
        if set(['salary', 'price', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - total_salary)/self.salary)
            return self.price * (len(self.workers) + needed_workers) * self.labor_productivity * \
                   (1 + 1 / self.demand_elasticity) - self.salary_budget
        return 0





