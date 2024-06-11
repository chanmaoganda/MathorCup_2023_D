from typing import List
from UtilClasses import DataStorage


class Instance:
    data: DataStorage
    
    def __init__(self, excavator_list: List[int], truck_list: List[int]):
        self.excavator_list = excavator_list
        self.truck_list = truck_list
        self.iteration = 0
        self.truck_number_dict = { truck: self.data.total_truck_numbers[truck] for truck in self.truck_list }

    
    def assign_iteration(self, iteration: int):
        self.iteration = iteration
        return self
        