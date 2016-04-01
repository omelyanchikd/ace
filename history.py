class History:
    def __init__(self, step_count):
        self.salaries = [0] * step_count
        self.prices = [0] * step_count
        self.workers_counts = [0] * step_count
        self.sales = [0] * step_count
        self.storage = [0] * step_count

    def add_record(self, step, firm):
        self.salaries[step] = firm.salary
        self.prices[step] = firm.price
        self.workers_counts[step] = len(firm.workers)
        self.sales[step] = firm.sales
        self.storage[step] = firm.stock
