
from typing import Dict, Tuple
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
    def __init__(self, used_excavator_numbers: Dict[str, ndarray], 
                 used_truck_numbers: Dict[str, ndarray], 
                 excavator_truck_usage: dict, 
                 half_used_excavator_bits: dict, 
                 cost_con_s: ndarray):
        self.used_excavator_numbers = used_excavator_numbers
        self.used_truck_numbers = used_truck_numbers
        self.excavator_truck_usage = excavator_truck_usage
        self.half_used_excavator_bits = half_used_excavator_bits
        self.cost_con_s = cost_con_s
    
    def unpack_variables(self) -> Tuple[Dict[str, ndarray], Dict[str, ndarray], dict, dict, ndarray] :
        """
        unpack used_excavator_numbers, used_truck_numbers, excavator_truck_usage, half_used_excavator_bits, cost_con_s
        """
        return self.used_excavator_numbers, self.used_truck_numbers, self.excavator_truck_usage, self.half_used_excavator_bits, self.cost_con_s