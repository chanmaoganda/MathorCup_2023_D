from typing import Dict, Generator

from numpy import ndarray
from Instance import Instance
from QuboUtil import QuboUtil
from utils import dict_key_checker, dict_type_checker


class GeneratorConstraintHandler:
    def __init__(self, qubo_util: QuboUtil, instance : Instance):
        self.qubo_util = qubo_util
        self.data = Instance.data

        
    def excavator_produce_expression_factory(self,
                                            excavator_numbers: Dict,
                                            half_used_excavator_bits: Dict) -> Generator:
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (20 * data.excavator_produce_efficiency[excavator_index] * (qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                                                - 0.5 * half_used_excavator_bits[f'excavator{excavator_index}_half_used']) 
                    for excavator_index in self.excavator_truck_dict.keys())
        return (0 for _ in self.excavator_truck_dict.keys())
    
    def oil_cost_expression_factory(self,
                                     excavator_numbers: Dict, 
                                     truck_numbers: Dict) -> Generator:
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (7 * (data.excavator_oil_consumption[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                         data.truck_oil_consumption[truck_index] * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}'])) 
                    for excavator_index, truck_index in self.excavator_truck_dict.items())
        
        if dict_type_checker(excavator_numbers, int, float):
            return (7 * (data.excavator_oil_consumption[excavator_index] * excavator_numbers[excavator_index] + 
                         data.truck_oil_consumption[truck_index] * truck_numbers[truck_index]) 
                    for excavator_index, truck_index in self.excavator_truck_dict.items())
        return (0 for _ in self.excavator_truck_dict.keys())
    
    def labor_maintenance_cost_expression_factory(self,
                                                  excavator_numbers: Dict, 
                                                  truck_numbers: Dict) -> Generator:
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return ((data.excavator_labor_cost[excavator_index] + data.excavator_maintenance_cost[excavator_index]) * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                    (data.truck_labor_cost[truck_index] + data.truck_maintenance_cost[truck_index]) * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}']) 
                    for excavator_index, truck_index in self.excavator_truck_dict.items())
        
        if dict_type_checker(excavator_numbers, int, float):
            return ((data.excavator_labor_cost[excavator_index] + data.excavator_maintenance_cost[excavator_index]) * excavator_numbers[excavator_index] + 
                    (data.truck_labor_cost[truck_index] + data.truck_maintenance_cost[truck_index]) * truck_numbers[truck_index] 
                    for excavator_index, truck_index in self.excavator_truck_dict.items())
        return (0 for _ in self.excavator_truck_dict.keys())
    
    def excavator_precurement_cost_expression_factory(self,
                                                     excavator_numbers: Dict) -> Generator:
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                    for excavator_index in self.excavator_truck_dict.keys())
        
        if dict_type_checker(excavator_numbers, int, float):
            return (data.excavator_precurement_cost[excavator_index] * excavator_numbers[excavator_index] 
                    for excavator_index in self.excavator_truck_dict.keys())
        return (0 for _ in self.excavator_truck_dict.keys())
    
    def total_revenue_expression_factory(self, produce, oil_consumption_cost, maintenance_cost, precurement_cost):
        return 160 * 60 * produce - 160 * 60 * oil_consumption_cost - 60 * maintenance_cost - 10000 * precurement_cost
    
    def object_expression_factory(self, total_revenue, budget_constraint, excavator_single_match_constraint: dict,
                                  truck_single_match_constraint: dict):
        qubo = self.qubo_util
        budget_param = 30000000000
        excavator_single_match_param = 100000000000
        truck_single_match_param = 100000000000
        if dict_key_checker(excavator_single_match_constraint, str):
            return - total_revenue + budget_param * budget_constraint + excavator_single_match_param * qubo.kaiwu_sum_proxy(
                excavator_single_match_constraint[f'excavator{excavator_index}_single_match_constraint']
                    for excavator_index in self.excavator_truck_dict.keys()) + truck_single_match_param * qubo.kaiwu_sum_proxy(
                truck_single_match_constraint[f'truck{truck_index}_single_match_constraint']
                    for truck_index in self.excavator_truck_dict.values())

        return 0