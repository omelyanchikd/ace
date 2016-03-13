class Worker:
    def __init__(self, id):
        self.id = id
        self.salary = 0
        self.employer = None
        self.productivity = 1

    # def work(self):
    #     print("I am a cool worker with id", self.id)
    #     if self.employer is not None:
    #         print("I am working for firm", self.employer, "with salary", self.salary)
    #     else:
    #         print("I am jobless, homeless and unhappy, so will work for food!")
