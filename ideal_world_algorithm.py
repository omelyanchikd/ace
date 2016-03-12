from world_algorithm import WorldAlgorithm
from firm_action import FirmAction
from firm_result import FirmResult
from worker import Worker


class IdealWorldAlgorithm(WorldAlgorithm):
    def apply(self, world, firm_id):
        """
        Ideal world! Everything is sold and new workers are everywhere.

        :type world: World
        :type firm_id: int
        """
        firm_action = world.firm_actions[firm_id]
        assert isinstance(firm_action, FirmAction)

        workers_count = firm_action.offer_count
        workers = []
        # here you have everyone non-employed
        for worker in world.workers:
            if worker.employer is None:
                workers.append(worker)
                workers_count -= 1
        # if it's not enough - here you have more!
        if workers_count > 0:
            for w in range(workers_count):
                new_worker_id = len(world.workers)
                worker = Worker(new_worker_id)
                world.workers.append(worker)
                workers.append(worker)
        # all your stuff is sold!
        sold_count = firm_action.sell_count
        return FirmResult(workers, sold_count)
