import csv
import math
import random

import ace.algorithms

from abc import ABCMeta, abstractmethod

from .service import match

from .firm_result import FirmResult
from .decision_maker import DecisionMaker
from .stats import Stats

from .firm_history import FirmHistory
from .labor_market_history import LaborMarketHistory

from .firm_labormarket_action import FirmLaborMarketAction



class Firm:
    __metaclass__ = ABCMeta

    def __init__(self, id, model_config, run_config, learning_method):
        self.id = id
        self.workers = set()
        self.stock = 0
        self.sold = 0
        self.sales = 0
        self.profit = 0
        self.total_salary = 0
        self.step = 0
        self.type = 'Unknown'
        self.decision_maker = DecisionMaker(id, self)
        self.history = FirmHistory(self)
        self.labor_market_history = LaborMarketHistory()
        self.control_parameters = [parameter for parameter in model_config if model_config[parameter]]
        if len(self.control_parameters) == 2 and set(['price', 'salary']).issubset(self.control_parameters):
            raise ValueError('It is impossible to derive other parameters only from salary and price in two-parameter case')
        self.derived_parameters = [parameter for parameter in model_config
                                   if model_config[parameter] is not None and not model_config[parameter]]
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
            if getattr(self, parameter) is None or getattr(self, parameter) == 0:
                setattr(self, parameter, self.derive(parameter, self.control_parameters))
        decision_maker = getattr(ace.algorithms, match(learning_method))
        self.decision_maker = decision_maker(id, self)


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
        self.total_salary = sum([worker.salary for worker in self.workers])
        if result != 0:
            self.sold = result.sold_count
            self.stock -= result.sold_count
            self.sales = self.price * result.sold_count
            self.profit = self.sales - self.total_salary
            if hasattr(self, 'raw'):
                self.profit -= self.raw_expenses
            if hasattr(self, 'capital'):
                self.profit -= self.capital_amortization * self.capital_expenses
            self.raw_expenses = 0
            self.money += self.sales
        else:
            self.profit = 0

    def add_worker(self, worker, salary):
        self.labor_market_history.add_record({'step': self.step, 'worker_id': worker.id,
                            'employer_id': self.id, 'action': 'hire', 'salary': salary})
        worker.employer = self.id
        worker.salary = salary
        worker.base_salary = salary
        worker.unemployment_period = 0
        self.workers.add(worker)

    def fire_worker(self, worker):
        self.labor_market_history.add_record({'step': self.step, 'worker_id': worker.id,
                            'employer_id': self.id, 'action': 'fire', 'salary': worker.salary})
        worker.employer = None
        worker.salary = 0
        self.workers.remove(worker)

    def remove_worker(self, worker):
        self.workers.remove(worker)

    def bankrupt(self):
        for worker in self.workers:
            worker.employer = None
            worker.salary = 0


    @abstractmethod
    def produce(self):
        for worker in self.workers:
            self.money -= worker.salary
            worker.money += worker.salary


    def decide(self, stats):
        pass

    def decide_price(self, stats):
        pass

    def decide_salary(self, stats):
        self.decision_maker.decide_salary(stats, self)
        if self.decision_maker.type not in ['DianaFirm', 'ExtrapolationFirm', 'OligopolyFirm', 'RationalFirm']:
            for parameter in self.derived_parameters:
                self.__setattr__(parameter, self.derive(parameter, self.control_parameters))
        while self.labor_capacity - len(self.workers) < 0:
            self.fire_worker(random.choice(list(self.workers)))
        return FirmLaborMarketAction(self.labor_capacity - len(self.workers), self.salary, [])

    def __str__(self):
        return str(self.id) + ' ' + self.type
        #return u"Firm id: {0:d}. Stock: {1:d} Price: {2:d} Money: {3:d} Workers: {4:d}" \
        #    .format(self.id, self.stock, self.price, self.money, len(self.workers))

    def __repr__(self):
        return self.__str__()


    def derive(self, parameter, control_parameters):
        return getattr(self, 'derive_' + parameter)(control_parameters)


    def derive_salary(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['price', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                value =  (self.price * self.plan  * (1 + 1 / self.demand_elasticity) - self.total_salary -
                raw_budget - capital_amortization * (capital_expenses + capital_budget))/needed_workers
                return value if value > 0 else 0.8 * self.salary
            return self.salary
        if set(['price', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
            if needed_workers > 0:
                value = (self.price * self.labor_capacity * self.labor_productivity  * (1 + 1 / self.demand_elasticity) -
                        self.total_salary - raw_budget - capital_amortization * (capital_expenses +
                                                                        capital_budget))/needed_workers
                return value if value > 0 else 0.8 * self.salary
            return self.salary
        if set(['price', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(raw_need * raw_productivity / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                value = (self.price * raw_need * raw_productivity  * (1 + 1 / self.demand_elasticity) -
                        self.total_salary - raw_budget - capital_amortization * (capital_expenses +
                                                                        capital_budget))/needed_workers
                return value if value > 0 else 0.8 * self.salary
            return self.salary
        if set(['price', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(capital_need * capital_productivity / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                value = (self.price * capital_need * capital_productivity  * (1 + 1 / self.demand_elasticity) -
                        self.total_salary - raw_budget - capital_amortization * (capital_expenses +
                                                                        capital_budget))/needed_workers
                return value if value > 0 else 0.8 * self.salary
            return self.salary
        if set(['plan', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
        elif set(['labor_capacity', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
        elif set(['raw_need', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor(raw_need * raw_productivity / self.labor_productivity) - len(self.workers)
        elif set(['price', 'raw_budget', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) * (1 + 1/self.demand_elasticity)) /
                                        (self.price * self.labor_productivity * (1 + 1/self.demand_elasticity)))
        if needed_workers > 0:
            value = (self.salary_budget - self.total_salary) / needed_workers
            return value if value > 0 else 0.8 * self.salary
        return self.salary


    def derive_price(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['salary', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) *  (self.total_salary + self.salary * needed_workers + raw_budget +
                    capital_amortization * (capital_budget + capital_expenses))/ self.plan
            return 1/(1 + 1/self.demand_elasticity) *  (self.total_salary + raw_budget +
                    capital_amortization * (capital_budget + capital_expenses))/ self.plan
        if set(['salary', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
            if needed_workers > 0:
                return 1/(1 + 1/self.demand_elasticity) *  (self.total_salary + self.salary * needed_workers + raw_budget +
                    capital_amortization * (capital_budget + capital_expenses))/ \
                       (self.labor_capacity * self.labor_productivity)
            return 1 / (1 + 1 / self.demand_elasticity) * (self.total_salary + raw_budget + capital_amortization *
                    (capital_budget + capital_expenses)) / (self.labor_capacity * self.labor_productivity)
        if set(['salary', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(raw_productivity * raw_need / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                return 1 / (1 + 1 / self.demand_elasticity) *  (self.total_salary + self.salary * needed_workers + raw_budget +
                    capital_amortization * (capital_budget + capital_expenses)) / \
                       (raw_need * raw_productivity)
            return 1 / (1 + 1 / self.demand_elasticity) * (self.total_salary + raw_budget +
            capital_amortization * (capital_budget + capital_expenses)) / \
                   (raw_need * raw_productivity)
        if set(['salary', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(capital_productivity * capital_need / self.labor_productivity) - len(self.workers)
            if needed_workers > 0:
                return 1 / (1 + 1 / self.demand_elasticity) *  (self.total_salary + self.salary * needed_workers + raw_budget +
                    capital_amortization * (capital_budget + capital_expenses)) / \
                       (capital_need * capital_productivity)
            return 1 / (1 + 1 / self.demand_elasticity) * (self.total_salary + raw_budget +
            capital_amortization * (capital_budget + capital_expenses)) / \
                   (capital_need * capital_productivity)
        if set(['plan', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            if self.plan > 0:
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                (capital_budget + capital_expenses)) / self.plan
            if self.stock > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                (capital_budget + capital_expenses)) / self.stock
            return self.price
        if set(['labor_capacity', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            if self.labor_capacity > 0:
                return 1/(1 + 1/self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                (capital_budget + capital_expenses)) / (self.labor_capacity * self.labor_productivity)
            if self.stock > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                        (capital_budget + capital_expenses)) / self.stock
            return self.price
        if set(['raw_need', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            if raw_need > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                (capital_budget + capital_expenses)) / (raw_need * raw_productivity)
            if self.stock > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                        (capital_budget + capital_expenses)) / self.stock
            return self.price
        if set(['capital_need', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            if capital_need > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                (capital_budget + capital_expenses)) / (capital_need * capital_productivity)
            if self.stock > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                    (capital_budget + capital_expenses)) / self.stock
            return self.price
        if set(['salary', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
            if needed_workers > 0 or len(self.workers) + needed_workers > 0:
                return 1 / (1 + 1 / self.demand_elasticity) * (self.salary_budget + raw_budget + capital_amortization *
                    (self.capital_budget + self.capital_expenses)) / ((len(self.workers) + needed_workers) * self.labor_productivity)
        return self.price


    def derive_plan(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['labor_capacity']).issubset(control_parameters):
            return math.floor(self.labor_capacity * self.labor_productivity)
        if set(['raw_need']).issubset(control_parameters):
            return math.floor(raw_need * raw_productivity)
        if set(['capital_need']).issubset(control_parameters):
            return math.floor(capital_need * capital_productivity)
        if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            try:
                needed_workers = math.floor((self.total_salary + raw_budget + capital_amortization * (capital_budget +
                capital_expenses) - (1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers) * self.price)/
                ((1 + 1/self.demand_elasticity) * self.labor_productivity * self.price - self.salary))
            except:
                needed_workers = 0
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
        elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) *
                (1 + 1 / self.demand_elasticity)) /(self.price * self.labor_productivity * (1 + 1 / self.demand_elasticity)))
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return math.floor((len(self.workers) + needed_workers) * self.labor_productivity)
        elif needed_workers != 0:
            return self.sold
        return 0


    def derive_labor_capacity(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['plan']).issubset(control_parameters):
            return math.floor(self.plan/ self.labor_productivity)
        if set(['raw_need']).issubset(control_parameters):
            return math.floor(raw_need * raw_productivity / self.labor_productivity)
        if set(['capital_need']).issubset(control_parameters):
            return math.floor(capital_need * capital_productivity/ self.labor_productivity)
        if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            try:
                needed_workers = math.floor((self.total_salary + raw_budget + capital_amortization * (capital_budget +
                capital_expenses) - (1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers) * self.price)/
                ((1 + 1/self.demand_elasticity) * self.labor_productivity * self.price - self.salary))
            except:
                needed_workers = 0
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
        elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) *
                (1 + 1 / self.demand_elasticity)) /(self.price * self.labor_productivity * (1 + 1 / self.demand_elasticity)))
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return (len(self.workers) + needed_workers)
        elif needed_workers != 0:
            return math.floor(self.sold/self.labor_productivity)
        return 0


    def derive_raw_need(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['labor_capacity']).issubset(control_parameters):
            return math.floor(self.labor_capacity * self.labor_productivity/raw_productivity)
        if set(['plan']).issubset(control_parameters):
            return math.floor(self.plan / raw_productivity)
        if set(['capital_need']).issubset(control_parameters):
            return math.floor(capital_need * capital_productivity/raw_productivity)
        if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.total_salary + raw_budget + capital_amortization * (capital_budget +
                capital_expenses) - (1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers) * self.price)/
                ((1 + 1/self.demand_elasticity) * self.labor_productivity * self.price - self.salary))
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
        elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) *
                (1 + 1 / self.demand_elasticity)) /(self.price * self.labor_productivity * (1 + 1 / self.demand_elasticity)))
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return math.floor((len(self.workers) + needed_workers) * self.labor_productivity/raw_productivity)
        return 0


    def derive_capital_need(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['labor_capacity']).issubset(control_parameters):
            return math.floor(self.labor_capacity * self.labor_productivity/capital_productivity)
        if set(['plan']).issubset(control_parameters):
            return math.floor(self.plan / capital_productivity)
        if set(['raw_need']).issubset(control_parameters):
            return math.floor(raw_need * raw_productivity/capital_productivity)
        if set(['salary', 'price', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.total_salary + raw_budget + capital_amortization * (capital_budget +
                capital_expenses) - (1 + 1/self.demand_elasticity) * self.labor_productivity * len(self.workers) * self.price)/
                ((1 + 1/self.demand_elasticity) * self.labor_productivity * self.price - self.salary))
        elif set(['salary', 'salary_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
        elif set(['price', 'salary_budget', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) *
                (1 + 1 / self.demand_elasticity)) /(self.price * self.labor_productivity * (1 + 1 / self.demand_elasticity)))
        if needed_workers > 0 or len(self.workers) + needed_workers > 0:
            return math.floor((len(self.workers) + needed_workers) * self.labor_productivity/capital_productivity)
        return 0


    def derive_salary_budget(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['price', 'plan', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * self.plan * (1 + 1 / self.demand_elasticity) - raw_budget - capital_amortization *\
                (capital_budget + capital_expenses)
        if set(['price', 'labor_capacity', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                raw_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['price', 'raw_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * raw_need * raw_productivity * (1 + 1 / self.demand_elasticity) - \
                raw_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['price', 'capital_need', 'raw_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * capital_need * capital_productivity * (1 + 1 / self.demand_elasticity) - \
                raw_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'plan']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
        elif set(['salary', 'labor_capacity']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity) - len(self.workers)
        elif set(['salary', 'raw_need']).issubset(control_parameters):
            needed_workers = math.floor(raw_need * raw_productivity / self.labor_productivity) - len(self.workers)
        elif set(['salary', 'capital_need']).issubset(control_parameters):
            needed_workers = math.floor(capital_need * capital_productivity / self.labor_productivity) - len(self.workers)
        elif set(['salary', 'price',  'raw_budget', 'capital_budget']).issubset(control_parameters):
            try:
                needed_workers = math.floor((self.salary_budget + raw_budget + capital_amortization *
                    (capital_expenses + capital_budget) - self.labor_productivity * self.price * len(self.workers) *
                    (1 + 1 / self.demand_elasticity)) / (self.price * self.labor_productivity * (1 + 1 / self.demand_elasticity)))
            except:
                needed_workers = 0
        if needed_workers > 0:
            return self.total_salary + self.salary * needed_workers
        return self.total_salary



    def derive_raw_budget(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']

        if set(['price', 'plan', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget -\
                   capital_amortization * (capital_budget + capital_expenses)
        if set(['price', 'labor_capacity', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['price', 'raw_need', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * raw_need * raw_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['price', 'capital_need', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            return self.price * capital_need * capital_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget - capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'plan', 'price', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            return self.price * self.plan * ( 1 + 1 / self.demand_elasticity) - self.total_salary - self.salary * needed_workers - \
                   capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'labor_capacity', 'price', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
            return self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
            self.total_salary - self.salary * needed_workers - capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'raw_need', 'price', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(raw_need * raw_productivity / self.labor_productivity) - len(self.workers)
            return self.price * raw_need * raw_productivity * (1 + 1 / self.demand_elasticity) - \
            self.total_salary - self.salary * needed_workers - capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'capital_need', 'price', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor(capital_need * capital_productivity / self.labor_productivity) - len(self.workers)
            return self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
            self.total_salary - self.salary * needed_workers - capital_amortization * (capital_budget + capital_expenses)
        if set(['salary', 'price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
            return self.price * (len(self.workers) + needed_workers) * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.salary_budget - capital_amortization * (capital_budget + capital_expenses)


    def derive_capital_budget(self, control_parameters):
        raw_budget = self.raw_budget if hasattr(self, 'raw') else 0
        raw_need = self.raw_need if hasattr(self, 'raw') else 0
        raw_productivity = self.raw_productivity if hasattr(self, 'raw') else 1
        capital_need = self.capital_need if hasattr(self, 'capital') else 0
        capital_budget = self.capital_budget if hasattr(self, 'capital') else 0
        capital_amortization = self.capital_amortization if hasattr(self, 'capital') else 0
        capital_expenses = self.capital_expenses if hasattr(self, 'capital') else 0
        capital_productivity = self.capital_productivity if hasattr(self, 'capital') else 1
        control_parameters = control_parameters + ['raw_budget', 'capital_budget']


        if set(['price', 'plan', 'salary_budget', 'raw_budget']).issubset(control_parameters):
            return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.salary_budget - \
                   raw_budget - capital_expenses * capital_amortization)/capital_amortization
        if set(['price', 'labor_capacity', 'salary_budget', 'raw_budget']).issubset(control_parameters):
            return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
            self.salary_budget - raw_budget - capital_expenses * capital_amortization)/ capital_amortization
        if set(['price', 'raw_need', 'salary_budget', 'raw_budget']).issubset(control_parameters):
            return (self.price * raw_need * raw_productivity * (1 + 1 / self.demand_elasticity) - \
            self.salary_budget - raw_budget - capital_expenses * capital_amortization)/capital_amortization
        if set(['price', 'capital_need', 'salary_budget', 'raw_budget']).issubset(control_parameters):
            return (self.price * capital_need * capital_productivity * (1 + 1 / self.demand_elasticity) -
                    self.salary_budget - raw_budget - capital_expenses * capital_amortization)/\
                   capital_amortization
        if set(['salary', 'plan', 'price', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.plan / self.labor_productivity) - len(self.workers)
            return (self.price * self.plan * (1 + 1 / self.demand_elasticity) - self.total_salary - \
            self.salary * needed_workers - raw_budget - capital_expenses * capital_amortization)/\
                   capital_amortization
        if set(['salary', 'labor_capacity', 'price', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor(self.labor_capacity - len(self.workers))
            return (self.price * self.labor_capacity * self.labor_productivity * (1 + 1 / self.demand_elasticity) - \
            self.total_salary - self.salary * needed_workers - raw_budget - capital_amortization * capital_expenses)/\
                   capital_amortization
        if set(['salary', 'raw_need', 'price', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor(raw_need * raw_productivity / self.labor_productivity) - len(self.workers)
            return (self.price * raw_need * raw_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.total_salary - self.salary * needed_workers - raw_budget - capital_expenses *
                    capital_amortization)/capital_amortization
        if set(['salary', 'capital_need', 'price', 'raw_budget']).issubset(control_parameters):
            needed_workers = math.floor(capital_need * capital_productivity / self.labor_productivity) - len(self.workers)
            return (self.price * self.capital_need * self.capital_productivity * (1 + 1 / self.demand_elasticity) - \
                   self.total_salary - self.salary * needed_workers - raw_budget - capital_amortization *
                   capital_expenses)/capital_amortization
        if set(['salary', 'price', 'salary_budget', 'capital_budget']).issubset(control_parameters):
            needed_workers = math.floor((self.salary_budget - self.total_salary) / self.salary)
            return (self.price * (len(self.workers) + needed_workers) * self.labor_productivity * (
            1 + 1 / self.demand_elasticity) - self.salary_budget - raw_budget - capital_amortization *
            capital_expenses)/capital_amortization





