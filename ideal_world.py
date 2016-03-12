from world import World
from firm_action import FirmAction
from firm_result import FirmResult
from worker import Worker


class IdealWorld(World):
    def apply_firm_action(self, firm_id):
        """
        Ideal world! Everything is sold and new workers are everywhere.

        :type firm_id: int
        """
        firm_action = self.firm_actions[firm_id]
        assert isinstance(firm_action, FirmAction)

        workers_count = firm_action.offer_count
        workers = []
        # here you have everyone non-employed
        for worker in self.workers:
            if worker.employer is None:
                workers.append(worker)
                workers_count -= 1
        # if it's not enough - here you have more!
        if workers_count > 0:
            for w in range(workers_count):
                new_worker_id = len(self.workers)
                worker = Worker(new_worker_id)
                self.workers.append(worker)
                workers.append(worker)
        # all your stuff is sold!
        sold_count = firm_action.sell_count
        return FirmResult(workers, firm_action.salary, sold_count)
