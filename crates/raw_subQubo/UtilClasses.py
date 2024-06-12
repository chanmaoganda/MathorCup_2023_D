from typing import Dict, List, Tuple
from numpy import ndarray

from QuboUtil import QuboUtil

class Constraints:
    def __init__(self, budget_constraint: ndarray, 
                    excavator_match_constraint_dict: Dict[str, ndarray], 
                    truck_match_constraint_dict: Dict[str, ndarray],
                    half_use_constraint_dict: dict):
        self.budget_constraint = budget_constraint
        self.excavator_match_constraint_dict = excavator_match_constraint_dict
        self.truck_match_constraint_dict = truck_match_constraint_dict
        self.half_use_constraint_dict = half_use_constraint_dict
    
    def unpack_constraints(self):
        """
        unpack budget_constraint, truck_num_constraint, excavator_single_match_constraint, truck_single_match_constraint
        """
        return self.budget_constraint, self.excavator_match_constraint_dict, self.truck_match_constraint_dict, self.half_use_constraint_dict
        
class Variables:
    def __init__(self, cost_constraint_num,
                 excavator_number_qubo_dict: Dict[int, ndarray],
                 truck_number_qubo_dict: Dict[int, ndarray],
                 excavator_truck_match_qubo_binary_dict: dict,
                 excavator_half_use_qubo_binary_dict: dict):
        self.cost_constraint_num = cost_constraint_num
        self.excavator_number_qubo_dict = excavator_number_qubo_dict
        self.truck_number_qubo_dict = truck_number_qubo_dict
        self.excavator_truck_match_qubo_binary_dict = excavator_truck_match_qubo_binary_dict
        self.excavator_half_use_qubo_binary_dict = excavator_half_use_qubo_binary_dict
        
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

class SolutionValue:
    def __init__(self, 
                 cost_constraint_num,
                 excavator_number_qubo_dict,
                 truck_number_qubo_dict,
                 excavator_truck_match_qubo_binary_dict,
                 excavator_half_use_qubo_binary_dict,
                 produce_value, 
                 oil_consumption_cost_value, 
                 maintenance_cost_value, 
                 precurement_cost_value, 
                 total_revenue_value, 
                 budget_constraint_value, 
                 excavator_match_constraint_dict_value, 
                 truck_match_constraint_dict_value, 
                 half_use_constraint_dict_value):
        self.cost_constraint_num = cost_constraint_num
        self.excavator_number_qubo_dict = excavator_number_qubo_dict
        self.truck_number_qubo_dict = truck_number_qubo_dict
        self.excavator_truck_match_qubo_binary_dict = excavator_truck_match_qubo_binary_dict
        self.excavator_half_use_qubo_binary_dict = excavator_half_use_qubo_binary_dict
        
        self.produce_value = produce_value
        self.oil_consumption_cost_value = oil_consumption_cost_value
        self.maintenance_cost_value = maintenance_cost_value
        self.precurement_cost_value = precurement_cost_value
        self.total_revenue_value = total_revenue_value
        self.budget_constraint_value = budget_constraint_value
        self.excavator_match_constraint_dict_value = excavator_match_constraint_dict_value
        self.truck_match_constraint_dict_value = truck_match_constraint_dict_value
        self.half_use_constraint_dict_value = half_use_constraint_dict_value
        
    def print_solution(self):
        print("Cost Constraint Num: ", self.cost_constraint_num)
        print("Excavator Number Qubo Dict: ", self.excavator_number_qubo_dict)
        print("Truck Number Qubo Dict: ", self.truck_number_qubo_dict)
        print("Excavator Truck Match Qubo Binary Dict: ", self.excavator_truck_match_qubo_binary_dict)
        print("Excavator Half Use Qubo Binary Dict: ", self.excavator_half_use_qubo_binary_dict)

        print("Produce Value: ", self.produce_value)
        print("Oil Consumption Cost Value: ", self.oil_consumption_cost_value)
        print("Maintenance Cost Value: ", self.maintenance_cost_value)
        print("Pre-Curement Cost Value: ", self.precurement_cost_value)
        print("Total Revenue Value: ", self.total_revenue_value)
        print("Budget Constraint Value: ", self.budget_constraint_value)
        print("Excavator Match Constraint Dict Value: ", self.excavator_match_constraint_dict_value)
        print("Truck Match Constraint Dict Value: ", self.truck_match_constraint_dict_value)
        print("Half Use Constraint Dict Value: ", self.half_use_constraint_dict_value)

class QuboSolution:
    """
    I need to store the solution of the problem, including VARIABLES and CONSTRAINTS.
    """
    def __init__(self,
                variables: Variables,
                produce,
                oil_consumption_cost,
                maintenance_cost,
                precurement_cost,
                total_revenue, 
                budget_constraint, 
                excavator_match_constraint_dict: Dict[str, ndarray], 
                truck_match_constraint_dict: Dict[str, ndarray],
                half_use_constraint_dict: dict):
        
        self.cost_constraint_num = variables.cost_constraint_num
        self.excavator_number_qubo_dict = variables.excavator_number_qubo_dict
        self.truck_number_qubo_dict = variables.truck_number_qubo_dict
        self.excavator_truck_match_qubo_binary_dict = variables.excavator_truck_match_qubo_binary_dict
        self.excavator_half_use_qubo_binary_dict = variables.excavator_half_use_qubo_binary_dict
        
        self.produce = produce
        self.oil_consumption_cost = oil_consumption_cost
        self.maintenance_cost = maintenance_cost
        self.precurement_cost = precurement_cost
        self.total_revenue = total_revenue
        self.budget_constraint = budget_constraint
        self.excavator_match_constraint_dict = excavator_match_constraint_dict
        self.truck_match_constraint_dict = truck_match_constraint_dict
        self.half_use_constraint_dict = half_use_constraint_dict
        
    def get_value_from_qubo_dict(self, qubo_dict) -> SolutionValue:
        qubo_util = QuboUtil()
        excavator_number_qubo_dict = qubo_util.read_dict_nums_from_dict(self.excavator_number_qubo_dict, qubo_dict)
        truck_number_qubo_dict = qubo_util.read_expr_dict_from_dict(self.truck_number_qubo_dict, qubo_dict)
        excavator_truck_match_qubo_binary_dict = qubo_util.read_bits_from_dict(self.excavator_truck_match_qubo_binary_dict, qubo_dict)
        excavator_half_use_qubo_binary_dict = qubo_util.read_bits_from_dict(self.excavator_half_use_qubo_binary_dict, qubo_dict)
        
        cost_constraint_num = qubo_util.read_num_from_dict(self.cost_constraint_num, qubo_dict)
        
        produce_value = qubo_util.get_val(self.produce, qubo_dict)
        oil_consumption_cost_value = qubo_util.get_val(self.oil_consumption_cost, qubo_dict)
        maintenance_cost_value = qubo_util.get_val(self.maintenance_cost, qubo_dict)
        precurement_cost_value = qubo_util.get_val(self.precurement_cost, qubo_dict)
        total_revenue_value = qubo_util.get_val(self.total_revenue, qubo_dict)
        budget_constraint_value = qubo_util.get_val(self.budget_constraint, qubo_dict)
        excavator_match_constraint_dict_value = qubo_util.read_constraint_from_dict(self.excavator_match_constraint_dict, qubo_dict)
        truck_match_constraint_dict_value = qubo_util.read_constraint_from_dict(self.truck_match_constraint_dict, qubo_dict)
        half_use_constraint_dict_value = qubo_util.read_constraint_from_dict(self.half_use_constraint_dict, qubo_dict)
        return SolutionValue(cost_constraint_num, excavator_number_qubo_dict, truck_number_qubo_dict, 
                             excavator_truck_match_qubo_binary_dict, excavator_half_use_qubo_binary_dict, 
                             produce_value, oil_consumption_cost_value, maintenance_cost_value, 
                             precurement_cost_value, total_revenue_value, 
                             budget_constraint_value, excavator_match_constraint_dict_value, 
                             truck_match_constraint_dict_value, half_use_constraint_dict_value)
        
