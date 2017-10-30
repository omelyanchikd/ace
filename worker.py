class Worker:
    def __init__(self, id):
        self.id = id
        self.step = 0
        self.salary = 0
        self.employer = None
        self.productivity = 1
        self.unemployment_period = 0
        self.base_salary = 0
        self.money = 0

    # def work(self):
    #     print("I am a cool worker with id", self.id)
    #     if self.employer is not None:
    #         print("I am working for firm", self.employer, "with salary", self.salary)
    #     else:
    #         print("I am jobless, homeless and unhappy, so will work for food!")
    def increment_step(self):
        self.step += 1
