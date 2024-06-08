from typing import List
from DataStorage import DataStorage


class Instance:
    def __init__(self, excavator_list: List[int], truck_list: List[int], data: DataStorage):
        """
        pass the excavator_list, truck_list and data to the InstanceSolver object
        data is from the instance maker (field -> data: DataStorage)
        """
        self.excavator_list = excavator_list
        self.truck_list = truck_list
        self.iteration = 0
        self.data = data
        self.truck_kind_dict = { truck: self.data.total_truck_numbers[truck] for truck in self.truck_list }

    
    def assign_iteration(self, iteration: int):
        self.iteration = iteration
        return self
        