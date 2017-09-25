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
        self.id = id
        self.stock = 0
        self.sold = 0
        self.price = 20
        self.money = 100000
        self.efficiency_coefficient = 10
        self.plan = 50
        self.current_salary = 200
        self.sales = 0
        self.salary = 200
        self.profit = 0
        self.output = output
        self.step = 0
        self.labor_capacity = 50
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
