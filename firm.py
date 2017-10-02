import csv
import math

from abc import ABCMeta, abstractmethod

from firm_result import FirmResult
from decision_maker import DecisionMaker
from stats import Stats


class Firm:
    __metaclass__ = ABCMeta

    def __init__(self, id, output = "output.csv"):
        self.workers = set()
        self.stock = 0
        self.sold = 0
        self.sales = 0
        self.profit = 0
        self.output = output
        self.step = 0
        self.type = 'Unknown'
        self.decision_maker = DecisionMaker(id, self)


    def apply_result(self, result):
        """

        :type result: FirmResult
        """
        self.salary = 0
        self.sales = 0
        for worker in result.quit_workers:
            self.remove_worker(worker)
        for worker in result.new_workers:
            self.add_worker(worker, result.salary)
        for worker in self.workers:
            self.salary += worker.salary
        self.sold = result.sold_count
        self.stock -= result.sold_count
        self.sales = self.price * result.sold_count
        self.profit = self.sales - self.salary
        if len(self.workers) > 0:
            self.salary /= len(self.workers)
        self.money += self.price * result.sold_count

    def apply_labormarket_result(self, result):
        if result != 0:
            for worker in result.quit_workers:
                self.remove_worker(worker)
            for worker in result.new_workers:
                self.add_worker(worker, result.salary)

    def apply_goodmarket_result(self, result):
        total_salary = 0
        for worker in self.workers:
            total_salary += worker.salary
        if result != 0:
            self.sold = result.sold_count
            self.stock -= result.sold_count
            self.sales = self.price * result.sold_count
            self.profit = self.sales - total_salary
            self.money += self.price * result.sold_count
        if len(self.workers) > 0:
            self.salary = total_salary / len(self.workers)

    def add_worker(self, worker, salary):
        worker.employer = self.id
        worker.salary = salary
        self.workers.add(worker)

    def fire_worker(self, worker):
        worker.employer = None
        worker.salary = 0
        self.workers.remove(worker)

    def remove_worker(self, worker):
        self.workers.remove(worker)

    def bankrupt(self):
        for worker in self.workers:
            worker.employer = None
            worker.salary = 0

    def save_history(self, stats):
        with open(self.output, "a", newline = '') as output_file:
            writer = csv.writer(output_file, delimiter = ';')
            writer.writerow((self.type, self.decision_maker.type, self.id, self.step, self.salary, len(self.workers), self.sold, self.price, self.stock, self.profit,
                             self.sold + self.stock, self.labor_capacity, self.sales, stats.price, stats.salary,
                            stats.sold, stats.sales, stats.money, stats.employed, stats.unemployment_rate
                            ))
            output_file.close()
        self.step += 1

    @abstractmethod
    def produce(self):
        pass

    def decide(self, stats):
        pass

    def decide_price(self, stats):
        pass

    def decide_salary(self, stats):
        pass

    def __str__(self):
        return str(self.id) + ' ' + self.type
        #return u"Firm id: {0:d}. Stock: {1:d} Price: {2:d} Money: {3:d} Workers: {4:d}" \
        #    .format(self.id, self.stock, self.price, self.money, len(self.workers))

    def __repr__(self):
        return self.__str__()


    def derive(self, parameter, control_parameters):
        return getattr(self, 'derive_' + parameter)(control_parameters)


    def derive_salary(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['price', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.plan  * (1 + 1 / self.demand_elasticity) - total_salary -
                    self.raw_budget - self.capital_amortization * (self.capital_expenses + self.capital_budget))/needed_workers
                return 0
            if set(['price', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.labor_capacity * self.labor_productivity  * (1 + 1 / self.demand_elasticity) -
                            total_salary - self.raw_budget - self.capital_amortization * (self.capital_expenses +
                                                                            self.capital_budget))/needed_workers
                return 0
            if set(['price', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.raw_need * self.raw_productivity  * (1 + 1 / self.demand_elasticity) -
                            total_salary - self.raw_budget - self.capital_amortization * (self.capital_expenses +
                                                                            self.capital_budget))/needed_workers
                return 0
            if set(['price', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.raw_need * self.raw_productivity  * (1 + 1 / self.demand_elasticity) -
                            total_salary - self.raw_budget - self.capital_amortization * (self.capital_expenses +
                                                                            self.capital_budget))/needed_workers
                return 0
            if set(['plan', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['raw_need', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
            elif set(['price', 'raw_budget', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget + self.raw_budget + self.capital_amortization *
                    (self.capital_expenses + self.capital_budget))/((1 + 1/self.demand_elasticity) * self.price *
                                                                    self.labor_productivity))
            else:
                return 0
            if needed_workers > 0:
                return (self.salary_budget - total_salary) / needed_workers
            return 0
        elif hasattr(self, 'capital'):
            if set(['price', 'plan', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.plan  * (1 + 1 / self.demand_elasticity) - total_salary -
                            self.capital_amortization * (self.capital_budget + self.capital_expenses))/needed_workers
                return 0
            if set(['price', 'labor_capacity', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) -
                    total_salary - self.capital_amortization * (self.capital_budget + self.capital_expenses)) / needed_workers
                return 0
            if set(['price', 'capital_need', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - \
                                 len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) -
                     total_salary - self.capital_amortization * (self.capital_budget + self.capital_expenses)) / needed_workers
                return 0
            if set(['plan', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['capital_need', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - \
                                 len(self.workers)
            elif set(['price', 'capital_budget', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(((self.salary_budget + self.capital_amortization * (self.capital_budget +
                    self.capital_expenses))/(1 + 1/self.demand_elasticity) - self.labor_productivity * self.price *
                        len(self.workers))/(self.price * self.labor_productivity))
            else:
                return 0
            if needed_workers > 0:
                return (self.salary_budget - total_salary) / needed_workers
        elif hasattr(self, 'raw'):
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
        else:
            if set(['price', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.plan - total_salary * 1 / (1 + 1 / self.demand_elasticity)) / \
                           (needed_workers / (1 + 1 / self.demand_elasticity))
                return 0
            if set(['price', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return (self.price * self.labor_capacity * self.labor_productivity -
                            total_salary * 1 / (1 + 1 / self.demand_elasticity)) / (
                           needed_workers / (1 + 1 / self.demand_elasticity))
                return 0
            if set(['plan', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
            elif set(['price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * self.salary_budget - self.labor_productivity *
                     self.price * len(self.workers)) / (self.labor_productivity * self.price))
            else:
                return 0
            if needed_workers > 0:
                return (self.salary_budget - total_salary) / needed_workers
        return 0


    def derive_price(self, control_parameters):
        total_salary = [worker.salary for worker in self.workers]
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['salary', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1/(1 + 1/self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses))/ \
                           self.plan
                return 0
            if set(['salary', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1/(1 + 1/self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses))/ \
                           (self.labor_capacity * self.labor_productivity)
                return 0
            if set(['salary', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_productivity * self.raw_need / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses)) / \
                           (self.raw_need * self.raw_productivity)
                return 0
            if set(['salary', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_productivity * self.capital_need / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers + self.raw_budget +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses)) / \
                           (self.capital_need * self.capital_productivity)
                return 0
            if set(['plan', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / self.plan
            if set(['labor_capacity', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / (self.labor_capacity * self.labor_productivity)
            if set(['raw_need', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / (self.raw_need * self.raw_productivity)
            if set(['capital_need', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / (self.capital_need * self.capital_productivity)
            if set(['salary', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget + self.capital_amortization *
                        (self.capital_budget + self.capital_expenses)) / ((len(self.workers) + needed_workers) * self.labor_productivity)
                return 0
        elif hasattr(self, 'capital'):
            if set(['salary', 'plan', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses)) / self.plan
                return 0
            if set(['salary', 'labor_capacity', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * ( total_salary + self.salary * needed_workers +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses)) / \
                           (self.labor_capacity * self.labor_productivity)
                return 0
            if set(['salary', 'capital_need', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_productivity * self.capital_need / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers +
                        self.capital_amortization * (self.capital_budget + self.capital_expenses)) / \
                           (self.capital_need * self.capital_productivity)
                return 0
            if set(['plan', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / self.plan
            if set(['labor_capacity', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / (self.labor_capacity * self.labor_productivity)
            if set(['capital_need', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget +self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / (self.capital_need * self.capital_productivity)
            if set(['salary', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.capital_amortization *
                        (self.capital_budget + self.capital_expenses)) / ((len(self.workers) + needed_workers) * self.labor_productivity)
                return 0
        elif hasattr(self, 'raw'):
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
        else:
            if set(['salary', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (
                    total_salary + self.salary * needed_workers) / self.plan
                return 0
            if set(['salary', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.salary * needed_workers) / \
                           (self.labor_capacity * self.labor_productivity)
                return 0
            if set(['plan', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                if needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * self.salary_budget / self.plan
                return 0
            if set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                if needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * self.salary_budget / (
                    self.labor_capacity * self.labor_productivity)
                return 0
            if set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                if needed_workers > 0:
                    return 1 / (1 + 1 / self.demand_elasticity) * self.salary_budget / (
                    self.labor_productivity * (len(self.workers) + needed_workers))
                return 0
        return 0


    def derive_plan(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity)
            if set(['raw_need']).issubset(control_parameters):
                return math.floor(self.raw_need * self.raw_productivity)
            if set(['capital_need']).issubset(control_parameters):
                return math.floor(self.capital_need * self.capital_productivity)
            if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.raw_budget +
                    self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers) -
                    1/(1 + 1/self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget +
                    self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                    self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        elif hasattr(self, 'capital'):
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity)
            if set(['capital_need']).issubset(control_parameters):
                return math.floor(self.capital_need * self.capital_productivity)
            if set(['salary', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.capital_amortization *
                    (self.capital_budget + self.capital_expenses)) - self.labor_productivity * self.price *
                    len(self.workers))/(self.labor_productivity * len(self.workers) - self.salary/(1 + 1/self.demand_elasticity)))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.capital_amortization *
                (self.capital_budget + self.capital_expenses)) - self.labor_productivity * self.price * len(self.workers))/
                                            (self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        elif hasattr(self, 'raw'):
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
        else:
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity)
            if set(['salary', 'price']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * total_salary - self.labor_productivity * self.price *
                     len(self.workers)) / (
                    self.labor_productivity * self.price - 1 / (1 + 1 / self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * self.salary_budget - self.labor_productivity * self.price *
                     len(self.workers)) / (self.price * self.labor_productivity))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        return 0


    def derive_labor_capacity(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan/ self.labor_productivity)
            if set(['raw_need']).issubset(control_parameters):
                return math.floor(self.raw_need * self.raw_productivity / self.labor_productivity)
            if set(['capital_need']).issubset(control_parameters):
                return math.floor(self.capital_need * self.capital_productivity / self.labor_productivity)
            if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.raw_budget +
                self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers) -
                    1/(1 + 1/self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.raw_budget +
                self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                   self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(len(self.workers) + needed_workers)
        elif hasattr(self, 'capital'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan/ self.labor_productivity)
            if set(['capital_need']).issubset(control_parameters):
                return math.floor(self.capital_need * self.capital_productivity / self.labor_productivity)
            if set(['salary', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (total_salary + self.capital_amortization *
                (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers) -
                    1/(1 + 1/self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1/(1 + 1/self.demand_elasticity) * (self.salary_budget + self.capital_amortization *
                (self.capital_budget + self.capital_expenses)) -
                   self.labor_productivity * self.price * len(self.workers))/(self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(len(self.workers) + needed_workers)
        elif hasattr(self, 'raw'):
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
        else:
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan / self.labor_productivity)
            if set(['salary', 'price']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * total_salary - self.labor_productivity * self.price *
                     len(self.workers)) / (
                    self.labor_productivity * self.price - 1 / (1 + 1 / self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * self.salary_budget - self.labor_productivity *
                     self.price * len(self.workers)) / (self.price * self.labor_productivity))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return len(self.workers) + needed_workers
        return 0


    def derive_raw_need(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan / self.raw_productivity)
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity / self.raw_productivity)
            if set(['capital_need']).issubset(control_parameters):
                return math.floor(self.capital_need * self.capital_productivity / self.raw_productivity)
            if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.raw_budget +
                self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                1 / (1 + 1 / self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget +
                    self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                     self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(
                    (len(self.workers) + needed_workers) * self.labor_productivity / self.raw_productivity)
        elif hasattr(self, 'raw'):
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
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget) -
                     self.labor_productivity * self.price * len(self.workers)) / (
                        self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(
                    (len(self.workers) + needed_workers) * self.labor_productivity / self.raw_productivity)
        return 0


    def derive_capital_need(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan / self.capital_productivity)
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity / self.capital_productivity)
            if set(['raw_need']).issubset(control_parameters):
                return math.floor(self.raw_need * self.raw_productivity / self.capital_productivity)
            if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1 / (1 + 1 / self.demand_elasticity) * (total_salary + self.raw_budget +
                self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                1 / (1 + 1 / self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + self.raw_budget +
                    self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                     self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(
                    (len(self.workers) + needed_workers) * self.labor_productivity / self.capital_productivity)
        elif hasattr(self, 'capital'):
            if set(['plan']).issubset(control_parameters):
                return math.floor(self.plan / self.capital_productivity)
            if set(['labor_capacity']).issubset(control_parameters):
                return math.floor(self.labor_capacity * self.labor_productivity / self.capital_productivity)
            if set(['salary', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((1 / (1 + 1 / self.demand_elasticity) * (total_salary +
                self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                1 / (1 + 1 / self.demand_elasticity) * self.salary))
            elif set(['salary', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
            elif set(['price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget +
                    self.capital_amortization * (self.capital_budget + self.capital_expenses)) -
                     self.labor_productivity * self.price * len(self.workers)) / (self.labor_productivity * len(self.workers)))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return math.floor(
                    (len(self.workers) + needed_workers) * self.labor_productivity / self.capital_productivity)
        return 0


    def derive_salary_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['price', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.raw_budget - self.capital_amortization *\
                    (self.capital_budget + self.capital_expenses)
            if set(['price', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                    self.raw_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['price', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                    self.raw_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['price', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                    self.raw_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['salary', 'raw_need']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'capital_need']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'price',  'raw_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1/(1 + self.demand_elasticity) * (total_salary + self.capital_amortization * (self.capital_budget +
                     self.capital_expenses) + self.raw_budget) - self.labor_productivity *
                     self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                        1/(1 + 1/self.demand_elasticity) * self.salary))
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return total_salary + self.salary * needed_workers
            return 0
        elif hasattr(self, 'capital'):
            if set(['price', 'plan', 'salary_budget']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget
            if set(['price', 'labor_capacity', 'salary_budget']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget
            if set(['price', 'capital_need', 'capital_budget']).issubset(control_parameters):
                return self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget
            if set(['salary', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity) - len(self.workers)
            elif set(['salary', 'capital_need']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1/(1 + self.demand_elasticity) * self.salary_budget - self.labor_productivity *
                     self.price * len(self.workers)) / (self.labor_productivity * len(self.workers) -
                                                        1/(1 + 1/self.demand_elasticity) * self.salary))
            else:
                return 0
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return total_salary + self.salary * needed_workers
            return 0
        elif hasattr(self, 'raw'):
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
        else:
            if set(['price', 'plan']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity)
            if set(['price', 'labor_capacity']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity)
            if set(['salary', 'plan']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            elif set(['salary', 'labor_capacity']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
            elif set(['salary', 'price']).issubset(control_parameters):
                needed_workers = math.floor(
                    (1 / (1 + 1 / self.demand_elasticity) * total_salary - self.labor_productivity * self.price *
                     len(self.workers)) / (self.price * self.labor_productivity))
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return total_salary + self.salary * needed_workers
        return 0


    def derive_raw_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['price', 'plan', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget -\
                       self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['price', 'labor_capacity', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['price', 'raw_need', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['price', 'capital_need', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                return self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'plan', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                return self.price * self.plan * ( 1 + 1 / self.demand_elasticity) - total_salary - self.salary * needed_workers - \
                       self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'labor_capacity', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'raw_need', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(
                    self.workers)
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'capital_need', 'price', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - len(
                    self.workers)
                return self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.capital_amortization * (self.capital_budget + self.capital_expenses)
            if set(['salary', 'price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                return self.price * (len(self.workers) + needed_workers) * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_amortization * (self.capital_budget + self.capital_expenses)
        elif hasattr(self, 'raw'):
            if set(['price', 'plan', 'salary_budget']).issubset(control_parameters):
                return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget
            if set(['price', 'labor_capacity', 'salary_budget']).issubset(control_parameters):
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget
            if set(['price', 'raw_need', 'salary_budget']).issubset(control_parameters):
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget
            if set(['salary', 'plan', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                return self.price * self.plan * (
                1 + 1 / self.demand_elasticity) - total_salary - self.salary * needed_workers
            if set(['salary', 'labor_capacity', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       total_salary - self.salary * needed_workers
            if set(['salary', 'raw_need', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(
                    self.workers)
                return self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                       total_salary - self.salary * needed_workers
            if set(['salary', 'price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                return self.price * (len(self.workers) + needed_workers) * self.labor_productivity * \
                       (1 + 1 / self.demand_elasticity) - self.salary_budget
        return 0


    def derive_capital_budget(self, control_parameters):
        total_salary = sum([worker.salary for worker in self.workers])
        if hasattr(self, 'raw') and hasattr(self, 'capital'):
            if set(['price', 'plan', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget - \
                       self.raw_budget - self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['price', 'labor_capacity', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                self.salary_budget - self.raw_budget - self.capital_expenses * self.capital_amortization)/ self.capital_amortization
            if set(['price', 'raw_need', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return (self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                self.salary_budget - self.raw_budget - self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['price', 'capital_need', 'salary_budget', 'raw_budget']).issubset(control_parameters):
                return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) -
                        self.salary_budget - self.raw_budget - self.capital_expenses * self.capital_amortization)/\
                       self.capital_amortization
            if set(['salary', 'plan', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - total_salary - \
                self.salary * needed_workers - self.raw_budget - self.capital_expenses * self.capital_amortization)/\
                       self.capital_amortization
            if set(['salary', 'labor_capacity', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.raw_budget - self.capital_amortization * self.capital_expenses)/\
                       self.capital_amortization
            if set(['salary', 'raw_need', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(self.raw_need * self.raw_productivity / self.labor_productivity) - len(
                    self.workers)
                return (self.price * self.raw_need * self.raw_productivity * (1 + 1 / self.demand_elasticity) - \
                       total_salary - self.salary * needed_workers - self.raw_budget - self.capital_expenses *
                        self.capital_amortization)/self.capital_amortization
            if set(['salary', 'capital_need', 'price', 'raw_budget']).issubset(control_parameters):
                needed_workers = math.floor(
                    self.capital_need * self.capital_productivity / self.labor_productivity) - len(
                    self.workers)
                return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                       total_salary - self.salary * needed_workers - self.raw_budget - self.capital_amortization *
                       self.capital_expenses)/self.capital_amortization
            if set(['salary', 'price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                return (self.price * (len(self.workers) + needed_workers) * self.labor_productivity * (
                1 + 1 / self.demand_elasticity) - self.salary_budget - self.raw_budget - self.capital_amortization *
                self.capital_expenses)/self.capital_amortization
        elif hasattr(self, 'capital'):
            if set(['price', 'plan', 'salary_budget']).issubset(control_parameters):
                return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget -
                self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['price', 'labor_capacity', 'salary_budget']).issubset(control_parameters):
                return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_expenses * self.capital_amortization) / self.capital_amortization
            if set(['price', 'capital_need', 'salary_budget']).issubset(control_parameters):
                return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                       self.salary_budget - self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['salary', 'plan', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
                return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - total_salary - self.salary * needed_workers -
                self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['salary', 'labor_capacity', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.labor_capacity - len(self.workers))
                return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['salary', 'capital_need', 'price']).issubset(control_parameters):
                needed_workers = math.floor(self.capital_need * self.capital_productivity / self.labor_productivity) - len(
                    self.workers)
                return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                total_salary - self.salary * needed_workers - self.capital_expenses * self.capital_amortization)/self.capital_amortization
            if set(['salary', 'price', 'salary_budget']).issubset(control_parameters):
                needed_workers = math.floor((self.salary_budget - total_salary) / self.salary)
                return (self.price * (len(self.workers) + needed_workers) * self.labor_productivity * \
                (1 + 1 / self.demand_elasticity) - self.salary_budget - self.capital_expenses * self.capital_amortization)/ \
                       self.capital_amortization
        return 0
