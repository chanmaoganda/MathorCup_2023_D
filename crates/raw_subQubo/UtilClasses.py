from typing import Dict, List, Tuple
from QuboUtil import QuboUtil
from numpy import ndarray

class Constraints:
    def __init__(self, budget_constraint: Dict[str, ndarray], 
                    truck_num_constraint: Dict[str, ndarray], 
                    excavator_single_match_constraint: Dict[str, ndarray], 
                    truck_single_match_constraint: Dict[str, ndarray]):
        self.budget_constraint = budget_constraint
        self.truck_num_constraint = truck_num_constraint
        self.excavator_single_match_constraint = excavator_single_match_constraint
        self.truck_single_match_constraint = truck_single_match_constraint
    
    def unpack_constraints(self):
        """
        unpack budget_constraint, truck_num_constraint, excavator_single_match_constraint, truck_single_match_constraint
        """
        return self.budget_constraint, self.truck_num_constraint, self.excavator_single_match_constraint, self.truck_single_match_constraint
        
class Variables:
    def __init__(self, cost_constraint_num: ndarray,
                 excavator_number_qubo_dict: Dict[int, ndarray],
                 truck_number_qubo_dict: Dict[int, ndarray],
                 excavator_truck_match_qubo_binary_dict: dict,
                 excavator_half_use_qubo_binary_dict: dict):
        self.excavator_number_qubo_dict = excavator_number_qubo_dict
        self.truck_number_qubo_dict = truck_number_qubo_dict
        self.excavator_truck_match_qubo_binary_dict = excavator_truck_match_qubo_binary_dict
        self.excavator_half_use_qubo_binary_dict = excavator_half_use_qubo_binary_dict
        
    def unpack(self) -> Tuple[Dict[int, ndarray], Dict[int, ndarray], dict, dict]:
        return self.excavator_number_qubo_dict, self.truck_number_qubo_dict, self.excavator_truck_match_qubo_binary_dict, self.excavator_half_use_qubo_binary_dict
        
class DataStorage:
    """
        this class only stores basic data for this problem, such as the budget, the oil consumption, the labor cost, the maintenance cost, etc.
    """
    def __init__(self, total_budget: int, 
                 excavator_bucket: List[float], excavator_efficiency: List[int], 
                 excavator_oil_consumption: List[int], truck_oil_consumption: List[int], 
                 excavator_labor_cost: List[int], truck_labor_cost: List[int], 
                 excavator_maintenance_cost: List[int], truck_maintenance_cost: List[int],
                 excavator_precurement_cost: List[int], excavators_trucks_match_dict: Dict[int, List[int]], 
                 total_truck_numbers: List[int]):

        self.total_budget = total_budget
        self.excavator_oil_consumption = excavator_oil_consumption
        self.truck_oil_consumption = truck_oil_consumption
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