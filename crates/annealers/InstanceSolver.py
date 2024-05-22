from DataStorage import DataStorage


class InstanceSolver:
    def __init__(self, excavator_list: list, data: DataStorage):
        self.excavator_list = excavator_list
        self.truck_list = [0, 1, 2]
        self.iteration = 0
        self.data = data
    
    def assign_iteration(self, iteration: int):
        self.iteration = iteration
        return self
        