from typing import List
from UtilClasses import DataStorage


class Instance:
    DATA: DataStorage = DataStorage(total_budget = 2400, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                                excavator_oil_consumption = [28,30,34,38], truck_oil_consumption = [18, 22, 27],
                                excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                                excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                                excavator_precurement_cost = [100, 140, 300, 320], 
                                excavators_trucks_match_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]},
                                total_truck_numbers = [7, 7, 3])
    
    def __init__(self, excavator_list: List[int], truck_list: List[int]):
        self.data = Instance.DATA
        self.excavator_list = excavator_list
        self.truck_list = truck_list
        self.iteration = 0
        self.truck_number_dict = { truck: self.data.total_truck_numbers[truck] for truck in self.truck_list }

    
    def assign_iteration(self, iteration: int):
        self.iteration = iteration
        return self
        