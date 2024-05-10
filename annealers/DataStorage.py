from typing import Dict, List

from QuboUtil import QuboUtil


class DataStorage:
    def __init__(self, total_budget: int, excavator_truck_dict: Dict[int, int], excavator_bucket: List[float], excavator_efficiency: List[int], excavator_oil_consumption: List[int], 
                 truck_oil_cosumption: List[int], excavator_labor_cost: List[int], truck_labor_cost: List[int], excavator_maintenance_cost: List[int], truck_maintenance_cost: List[int],
                 excavator_precurement_cost: List[int], excavators_trucks_match_dict: Dict[int, List[int]], total_truck_numbers: List[int]):
        self.total_budget = total_budget
        self.excavator_truck_dict = excavator_truck_dict
        self.excavator_oil_consumption = excavator_oil_consumption
        self.truck_oil_cosumption = truck_oil_cosumption
        self.excavator_labor_cost = excavator_labor_cost
        self.truck_labor_cost = truck_labor_cost
        self.excavator_maintenance_cost = excavator_maintenance_cost
        self.truck_maintenance_cost = truck_maintenance_cost
        self.excavator_precurement_cost = excavator_precurement_cost
        
        self.workdays_per_month = 20
        self.workhours_per_day = 8
        self.oil_price = 7
        self.mineral_price = 10

        self.excavators_trucks_match_dict : Dict[int, List[int]] = excavators_trucks_match_dict
        self.total_truck_numbers = total_truck_numbers
        
        self.excavator_kinds = len(self.excavators_trucks_match_dict.keys())
        self.truck_kinds = len(self.excavators_trucks_match_dict[0]) # any element in the dictionary matches the number of truck_kinds
        
        self.excavator_produce_efficiency = list(( excavator_bucket[index] * excavator_efficiency[index] for index in range(self.excavator_kinds)))