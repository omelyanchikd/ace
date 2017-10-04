import csv
import random

from abc import ABCMeta

import algorithms
import stats

from history import History
from worker import Worker





class World:
    __metaclass__ = ABCMeta

    def __init__(self, model_config, run_config):

        self.firms = []
        firm_count = 0
        #if model_config['raw_firm_structure'] is not None:
        self.raw_firms = []
        for learning_item in run_config['raw_firm_config']['learnings']:
            for i in range(int(learning_item['count'])):
                firm = algorithms.RawFirm(firm_count, model_config['raw_firm_structure'], run_config['raw_firm_config'], learning_item['method'])
                self.raw_firms.append(firm)
                self.firms.append(firm)
                firm_count += 1

        if model_config['capital_firm_structure'] is not None:
            self.capital_firms = []
            for learning_item in run_config['capital_firm_config']['learnings']:
                for i in range(int(learning_item['count'])):
                    firm = algorithms.CapitalFirm(firm_count, model_config['capital_firm_structure'], run_config['capital_firm_config'], learning_item['method'])
                    self.capital_firms.append(firm)
                    self.firms.append(firm)
                    firm_count += 1


        self.production_firms = []
        for learning_item in run_config['production_firm_config']['learnings']:
            for i in range(int(learning_item['count'])):
                firm = algorithms.ProductionFirm(firm_count, model_config['production_firm_structure'], run_config['production_firm_config'], learning_item['method'])
                self.production_firms.append(firm)
                self.firms.append(firm)
                firm_count += 1



        if model_config['government_structure'] is not None:
            self.government = algorithms.Government(model_config['government_structure'], run_config['government_config'])

        if model_config['outside_world']:
            self.outside_world = algorithms.OutsideWorld(run_config['outside_world_config'])


        self.stats = stats.Stats()

        self.money = run_config['initial_money']
        self.steps = run_config['iterations']

        self.birth_rate = run_config['household_birth']
        self.money_growth = run_config['money_growth']

        self.model_config = model_config
        self.run_config = run_config

        #self.firm_algorithms = config['algorithms']
        household_count = run_config['household_config']['count']
        self.households = []

        firm_count = len(self.firms)

        # initial worker distribution
        for i in range(household_count):
            worker = Worker(i)
            self.households.append(worker)
            if sum([len(firm.workers) - firm.labor_capacity for firm in self.firms]):
                while True:
                    employer = random.choice(self.firms)
                    if employer.labor_capacity > len(employer.workers):
                        firm.add_worker(self.households[i], firm.salary)
                        break

        self.history = History(self.steps, self.firms)

        self.firm_actions = [0] * firm_count
        self.firm_results = [0] * firm_count

        self.firm_labormarket_actions = [0] * firm_count
        self.firm_goodmarket_actions = [0] * firm_count

        self.firm_labormarket_results = [0] * firm_count
        self.firm_goodmarket_results = [0] * firm_count

        with open("output.csv", "w", newline='') as output_file:
            writer = csv.DictWriter(output_file, delimiter=';',
                                    fieldnames=["firm_type", "learning_type", "firm_id", "step", "salary", "workers", "sold", "price", "stock", "profit",
                                                "product_supply", "labor_demand", "sales", "world_price", "world_salary", "world_sold",
                                                "world_sales", "world_money", "world_employed", "world_unemployment_rate"])
            writer.writeheader()
            output_file.close()

    def manage_firm_actions(self, firm_actions, firm_type):
        pass

    def manage_sales(self, firm_type):
        pass

    def manage_job_offers(self, firm_type):
        pass

    def go(self):
        print("It's alive!!")
        for step in range(self.steps):
            # print("Step:", step)
            for i, firm in enumerate(self.raw_firms):
                firm.produce()
                self.firm_goodmarket_actions[firm.id] = firm.decision_maker.decide_price(self.stats, firm)
            self.manage_sales('RawFirm')
            for i, firm in enumerate(self.capital_firms):
                firm.produce()
                self.firm_goodmarket_actions[firm.id] = firm.decision_maker.decide_price(self.stats, firm)
            self.manage_sales('CapitalFirm')
            for i, firm in enumerate(self.production_firms):
                # @todo: enable bankrupt
                # if firm.money < self.config['global']['bankrupt_rate']:
                #     firm.bankrupt()
                #     del self.firms[i]
                #     del self.firm_actions[i]
                #     continue
                # print(firm)
                firm.produce()
                # print(firm)
                self.firm_goodmarket_actions[firm.id] = firm.decision_maker.decide_price(self.stats, firm)
            self.manage_sales('ProductionFirm')
            for firm_id, firm_action in enumerate(self.firm_goodmarket_actions):
                firm = self.firms[firm_id]
                firm.apply_goodmarket_result(self.firm_goodmarket_results[firm_id])
                firm.save_history(self.stats)
                self.history.add_record(step, firm)
            self.stats.get_stats(self)
            self.history.add_stats(step, self.stats)  # needs to be rewritten with proper history object in mind
            for j in range(self.birth_rate):
                worker = Worker(len(self.households))
                self.households.append(worker)
            for i, firm in enumerate(self.firms):
                self.firm_labormarket_actions[firm.id] = firm.decide_salary(self.stats)
            self.manage_job_offers()
            for firm_id, firm_action in enumerate(self.firm_labormarket_actions):
                firm = self.firms[firm_id]
                firm.apply_labormarket_result(self.firm_labormarket_results[firm_id])
            self.money += self.money_growth

        return self.history
