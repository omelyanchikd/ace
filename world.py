import csv

from abc import ABCMeta

import algorithms

from history import History
from worker import Worker
from stats import Stats

from government import Government
from outside_world import OutsideWorld
from raw_firm import RawFirm
from firm_action import FirmAction
from firm_goodmarket_action import FirmGoodMarketAction
from firm_labormarket_action import FirmLaborMarketAction



class World:
    __metaclass__ = ABCMeta

    def __init__(self, model_config, run_config):

        firm_counter = 0
        if model_config['raw_firm_structure'] is not None:
            self.raw_firms = []
            for learning_method, count in run_config['raw_firm_config']:
                for i in range(int(count)):
                    #firm_class = getattr(algorithms, class_)
                    #firm = firm_class(firm_counter)
                    firm = RawFirm(model_config['raw_firm_structure', run_config['raw_firm_config']], learning_method)
                    self.raw_firms.append(firm)
                    firm_counter += 1

        if model_config['capital_firm_structure'] is not None:
            self.capital_firms = []

        self.production_firms = []
        self.households = []

        if model_config['government'] is not None:
            self.government = Government(model_config['government'], run_config['government'])

        if model_config['outside_world']:
            self.outside_world = OutsideWorld(run_config['government'])


        self.stats = Stats()

        self.money = run_config['initial_money']
        self.steps = run_config['iterations']

        #self.firm_algorithms = config['algorithms']
        household_count = run_config['households_count']
        self.model_config = model_config
        self.run_config = run_config
        firm_counter = 0

        for class_, count in self.firm_algorithms.items():
            for i in range(int(count)):
                firm_class = getattr(algorithms, class_)
                firm = firm_class(firm_counter)
                self.firms.append(firm)
                firm_counter += 1
        firm_count = firm_counter
        # initial worker distribution
        for i in range(workers_count):
            worker = Worker(i)
            self.workers.append(worker)
            firm_id = i % firm_count
            firm = self.firms[firm_id]
            firm.add_worker(worker, firm.current_salary)

        self.history = History(self.steps, self.firms)

        self.firm_actions = [0] * firm_count
        self.firm_results = [0] * firm_count

        self.firm_labormarket_actions = [0] * firm_count
        self.firm_goodmarket_actions = [0] * firm_count

        self.firm_labormarket_results = [0] * firm_count
        self.firm_goodmarket_results = [0] * firm_count

        with open(run_config['global']['output'], "w", newline='') as output_file:
            writer = csv.DictWriter(output_file, delimiter=';',
                                    fieldnames=["firm_type", "firm_id", "step", "salary", "workers", "sold", "price", "stock", "profit",
                                                "product_supply", "labor_demand", "sales", "world_price", "world_salary", "world_sold",
                                                "world_sales", "world_money", "world_employed", "world_unemployment_rate"])
            writer.writeheader()
            output_file.close()

    def manage_firm_actions(self, firm_actions):
        pass

    def manage_sales(self):
        pass

    def manage_job_offers(self):
        pass

    def compute_stats(self):
        self.stats.f = len(self.firms)
        self.stats.price = 0
        self.stats.stock = 0
        self.stats.sales = 0
        self.stats.sold = 0
        self.stats.salary = 0
        self.employed = 0
        for firm in self.firms:
            self.stats.stock += firm.stock
            self.stats.sold += firm.sold
            self.stats.sales += firm.sales
            self.employed += len(firm.workers)
            for worker in firm.workers:
                self.stats.salary += worker.salary
        if self.stats.sold > 0:
            self.stats.price = self.stats.sales / self.stats.sold
        else:
            self.stats.price = 0
        if self.employed > 0:
            self.stats.salary /= self.employed
        else:
            self.stats.salary = 0
        unemployed = 0
        for worker in self.workers:
            if worker.employer is None:
                unemployed += 1
        if len(self.workers) > 0:
            self.stats.unemployment_rate = unemployed / len(self.workers)
        self.stats.money = self.money
#        self.stats.expected_sales_growth = self.config['global']['money_growth']/self.money
        self.stats.expected_sold_growth = 0.05

    def go(self):
        print("It's alive!!")
        birth_rate = self.config['global']['birth_rate']
        money_growth = self.config['global']['money_growth']
        for step in range(self.steps):
            # print("Step:", step)
            for i, firm in enumerate(self.firms):
                # @todo: enable bankrupt
                # if firm.money < self.config['global']['bankrupt_rate']:
                #     firm.bankrupt()
                #     del self.firms[i]
                #     del self.firm_actions[i]
                #     continue
                # print(firm)
                firm.work()
                # print(firm)
                self.firm_goodmarket_actions[firm.id] = firm.decide_price(self.stats)
            self.manage_sales()
            for firm_id, firm_action in enumerate(self.firm_goodmarket_actions):
                firm = self.firms[firm_id]
                firm.apply_goodmarket_result(self.firm_goodmarket_results[firm_id])
                firm.save_history(self.stats)
                self.history.add_record(step, firm)
            self.compute_stats()
            self.history.add_stats(step, self.stats)  # needs to be rewritten with proper history object in mind
            for j in range(birth_rate):
                worker = Worker(len(self.workers))
                self.workers.append(worker)
            for i, firm in enumerate(self.firms):
                self.firm_labormarket_actions[firm.id] = firm.decide_salary(self.stats)
            self.manage_job_offers()
            for firm_id, firm_action in enumerate(self.firm_labormarket_actions):
                firm = self.firms[firm_id]
                firm.apply_labormarket_result(self.firm_labormarket_results[firm_id])
            self.money += money_growth

        return self.history
