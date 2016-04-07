from world_history import WorldHistory
from firm_history import FirmHistory

class History:
    def __init__(self, step_count, firms):
        self.firms_history = [FirmHistory(firms[i].__class__.__name__ + str(i), step_count) for i in range(len(firms))]

        self.world_history = WorldHistory(step_count)

    def add_record(self, step, firm):
        self.firms_history[firm.id].add_record(step, firm)

    def add_stats(self, step, stats):
        self.world_history.add_stats(step, stats)
