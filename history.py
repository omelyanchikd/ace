class History:
    def __init__(self, step_count, name):
        self.title = name
        self.salaries = [0] * step_count
        self.prices = [0] * step_count
        self.workers_counts = [0] * step_count
        self.sales = [0] * step_count
        self.storage = [0] * step_count
        self.profits = [0] * step_count
        self.money = [0] * step_count
        self.sold = [0] * step_count

        self.world_money = [0] * step_count
        self.world_price = [0] * step_count
        self.world_sold = [0] * step_count
        self.world_sales = [0] * step_count
        self.world_salary = [0] * step_count
        self.unemployment_rate = [0] * step_count

    def add_record(self, step, firm):
        self.salaries[step] = firm.salary
        self.prices[step] = firm.price
        self.workers_counts[step] = len(firm.workers)
        self.sales[step] = firm.sales
        self.storage[step] = firm.stock
        self.profits[step] = firm.profit
        self.money[step] = firm.money
        self.sold[step] = firm.sold

    def add_stats(self, step, stats):
        self.world_money[step] = stats.money
        self.world_price[step] = stats.price
        self.world_sold[step] = stats.sold
        self.world_sales[step] = stats.sales
        self.world_salary[step] = stats.salary
        self.unemployment_rate[step] = stats.unemployment_rate
