class WorldHistory:
    def __init__(self, step_count):
        self.title = "World"
        self.money = [0] * step_count
        self.price = [0] * step_count
        self.sold = [0] * step_count
        self.sales = [0] * step_count
        self.salary = [0] * step_count
        self.unemployment_rate = [0] * step_count

    def add_stats(self, step, stats):
        self.money[step] = stats.money
        self.price[step] = stats.price
        self.sold[step] = stats.sold
        self.sales[step] = stats.sales
        self.salary[step] = stats.salary
        self.unemployment_rate[step] = stats.unemployment_rate
