class History:
    def __init__(self, step_count):
        self.salaries = [0] * step_count
        self.prices = [0] * step_count
        self.workers_counts = [0] * step_count

    def add_record(self, step, firm):
        self.salaries[step] = firm.current_salary
        self.prices[step] = firm.price
        self.workers_counts[step] = len(firm.workers)
