import ace.world

class Stats:
    def __init__(self):
        self.step = 0
        for type in ['raw_', 'capital_', 'production_','']:
            for variable in ['price', 'salary', 'sold', 'stock', 'sales', 'money', 'labor_capacity', 'employed', 'total_salary', 'salary_budget']:
                setattr(self, type + variable, 0)
        self.unemployment_rate = 0
        for type in ['raw', 'capital']:
            for variable in ['', '_need', '_budget', '_expenses']:
                setattr(self, type + variable, 0)
        self.expected_sales_growth = 0
        self.expected_sold_growth = 0
        for type in ['raw_', 'capital_', 'production_', '']:
            setattr(self, type + 'firms', 0)
        self.households = 0


    def get_stats(self, world):
        self.__init__()
        self.step = world.step
        for type in ['raw_', 'capital_', 'production_', '']:
            setattr(self, type + 'firms', len(getattr(world, type + 'firms')))
        self.households = len(world.households)
        unemployed = 0
        for worker in world.households:
            if worker.employer is None:
                unemployed += 1
        if len(world.households) > 0:
            self.unemployment_rate = unemployed / len(world.households)
        for type in ['raw', 'capital', 'production']:
            self.get_firm_stats(world, type)
        if self.sold > 0:
            self.price = self.sales / self.sold
        else:
            self.price = 0
        if self.employed > 0:
            self.salary = self.total_salary / self.employed
        else:
            self.salary = 0
        self.expected_sales_growth = world.money_growth/world.money
        self.expected_sold_growth = 0.01


    def get_firm_stats(self, world, type):
        for firm in world.__getattribute__(type + '_firms'):
            for variable in ['sold', 'sales', 'stock', 'money', 'salary_budget', 'labor_capacity', 'total_salary']:
                self.__setattr__(type + '_' + variable,  self.__getattribute__(type + '_' + variable) + getattr(firm, variable))
                self.__setattr__(variable, self.__getattribute__(variable) + getattr(firm, variable))
            self.employed += len(firm.workers)
            self.__setattr__(type + '_employed', self.__getattribute__(type + '_employed') + len(firm.workers))
            for attribute in ['raw', 'capital']:
                if hasattr(firm, attribute):
                    for variable in ['', '_budget', '_need', '_expenses']:
                        self.__setattr__(attribute + variable, self.__getattribute__(attribute + variable) +
                                getattr(firm, attribute + variable))
        if self.__getattribute__(type + '_sold') > 0:
            self.__setattr__(type + '_price', self.__getattribute__(type + '_sales') / self.__getattribute__(type + '_sold'))
        else:
            self.__setattr__(type + '_price', 0)
        if self.__getattribute__(type + '_employed') > 0:
            self.__setattr__(type + '_salary', self.__getattribute__(type + '_total_salary') /
                             self.__getattribute__(type + '_employed'))
        else:
            self.__setattr__(type + '_salary', 0)


