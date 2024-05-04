from typing import Dict

from numpy import ndarray
from DataStorage import DataStorage
from QuboUtil import QuboUtil
from utils import dict_type_checker


class GeneratorConstraintHandler:
    def __init__(self, qubo_util: QuboUtil, data: DataStorage):
        self.qubo_util = qubo_util
        self.data = data
        
    def excavator_produce_expression_factory(self,
                                            excavator_numbers: Dict,
                                            half_used_excavator_bits: Dict):
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (20 * data.excavator_produce_efficiency[excavator_index] * (qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                                                - 0.5 * half_used_excavator_bits[f'excavator{excavator_index}_half_used']) 
                    for excavator_index in data.excavator_truck_dict.keys())
        
        elif dict_type_checker(excavator_numbers, int, float):
            return (20 * data.excavator_produce_efficiency[excavator_index] * (excavator_numbers[excavator_index] 
                                                -0.5 * half_used_excavator_bits[excavator_index]) 
                    for excavator_index in data.excavator_truck_dict.keys())
        return (0 for _ in data.excavator_truck_dict.keys())
    
    def oil_cost_expression_factory(self,
                                     excavator_numbers: Dict, 
                                     truck_numbers: Dict):
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (7 * (data.excavator_oil_consumption[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                         data.truck_oil_cosumption[truck_index] * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}'])) 
                    for excavator_index, truck_index in data.excavator_truck_dict.items())
        
        elif dict_type_checker(excavator_numbers, int, float):
            return (7 * (data.excavator_oil_consumption[excavator_index] * excavator_numbers[excavator_index] + 
                         data.truck_oil_cosumption[truck_index] * truck_numbers[truck_index]) 
                    for excavator_index, truck_index in data.excavator_truck_dict.items())
        return (0 for _ in data.excavator_truck_dict.keys())
    
    def labor_maintenance_cost_expression_factory(self,
                                                  excavator_numbers: Dict, 
                                                  truck_numbers: Dict):
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return ((data.excavator_labor_cost[excavator_index] + data.excavator_maintenance_cost[excavator_index]) * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                    (data.truck_labor_cost[truck_index] + data.truck_maintenance_cost[truck_index]) * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}']) 
                    for excavator_index, truck_index in data.excavator_truck_dict.items())
        
        elif dict_type_checker(excavator_numbers, int, float):
            return ((data.excavator_labor_cost[excavator_index] + data.excavator_maintenance_cost[excavator_index]) * excavator_numbers[excavator_index] + 
                    (data.truck_labor_cost[truck_index] + data.truck_maintenance_cost[truck_index]) * truck_numbers[truck_index] 
                    for excavator_index, truck_index in data.excavator_truck_dict.items())
        return (0 for _ in data.excavator_truck_dict.keys())
    
    def excavator_precurement_cost_expression_factory(self,
                                                     excavator_numbers: Dict, 
                                                     half_used_excavator_bits: Dict):
        data = self.data
        qubo = self.qubo_util
        if dict_type_checker(excavator_numbers, str, ndarray):
            return (data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                    for excavator_index in data.excavator_truck_dict.keys())
        
        elif dict_type_checker(excavator_numbers, int, float):
            return (data.excavator_precurement_cost[excavator_index] * excavator_numbers[excavator_index] 
                    for excavator_index in data.excavator_truck_dict.keys())
        return (0 for _ in data.excavator_truck_dict.keys())
    
    def revenue_expression_factory(self,
                                    excavator_numbers: Dict[str, ndarray], 
                                    truck_numbers: Dict[str, ndarray], 
                                    half_used_excavator_bits: Dict[str, ndarray], 
                                    cost_con_val):
        qubo = self.qubo_util
        data = self.data
        big_number = 1000000
        
        excavator_produce_efficiency = data.excavator_produce_efficiency
        produce_expression_generator = (20 * excavator_produce_efficiency[excavator_index] * (qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                                            - 0.5 * half_used_excavator_bits[f'excavator{excavator_index}_half_used']) 
                        for excavator_index in data.excavator_truck_dict.keys())
        
        oil_cost_expression_generator = (
            7 * (
                data.excavator_oil_consumption[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                data.truck_oil_cosumption[truck_index] * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}'])
            )
            for excavator_index, truck_index in data.excavator_truck_dict.items())
        
        labor_maintenance_cost_expression_generator = (
            (data.excavator_labor_cost[excavator_index] + data.excavator_maintenance_cost[excavator_index]) * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
            (data.truck_labor_cost[truck_index] + data.truck_maintenance_cost[truck_index]) * qubo.make_qubo_ndarray_sum(truck_numbers[f'truck{truck_index}']) 
            for excavator_index, truck_index in data.excavator_truck_dict.items())
        
        excavator_precurement_cost_expression_generator = (
            data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}'])
            for excavator_index in data.excavator_truck_dict.keys())
        
        produce = qubo.kaiwu_sum_proxy(produce_expression_generator)
        oil_consume = qubo.kaiwu_sum_proxy(oil_cost_expression_generator)
        maintenance = qubo.kaiwu_sum_proxy(labor_maintenance_cost_expression_generator)
        precurement = qubo.kaiwu_sum_proxy(excavator_precurement_cost_expression_generator)
        
        total_revenue = 160 * 60 * produce - 160 * 60 * oil_consume - 60 * maintenance - 10000 * precurement