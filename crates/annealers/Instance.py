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
        self.data = data
        self.excavator_truck_dict =  { excavator: truck for excavator, truck in 
                            zip(self.excavator_list, self.truck_list) }
    
    def assign_iteration(self, iteration: int):
        self.iteration = iteration
        return self
        