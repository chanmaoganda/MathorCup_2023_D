from calendar import c
from typing import Dict

from numpy import half, ndarray
from DataStorage import DataStorage
from QuboUtil import QuboUtil
from utils import *

class JobShopWithArgs:
    def __init__(self, excavators: list, trucks: list):
        self.excavator_truck_dict: Dict[int, int] = { excavator: truck for excavator, truck in zip(excavators, trucks)}
        self.data = DataStorage(total_budget = 2400, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                                excavator_oil_consumption = [28,30,34,38], truck_oil_cosumption = [18, 22, 27],
                                excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                                excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                                excavator_precurement_cost = [100, 140, 300, 320], 
                                excavator_truck_match_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]},
                                total_truck_numbers = [7, 7, 3])
        self.qubo_util = QuboUtil()

    def solve(self):
        excavator_numbers, fully_used_truck_numbers, half_used_excavator_bits, cost_con_s = self.init_quantum_variables()
        print(f'current used bits are {self.qubo_util.total_bits}')
        budget_constraint, truck_num_constraint = self.make_qubo_constraints(excavator_numbers, fully_used_truck_numbers, half_used_excavator_bits, cost_con_s)

        total_revenue, object, produce, oil_consume, maintenance, precurement = self.generate_qubo_model(excavator_numbers, fully_used_truck_numbers, half_used_excavator_bits, budget_constraint, truck_num_constraint)
        self.print_solution(object, total_revenue, excavator_numbers, fully_used_truck_numbers, half_used_excavator_bits, cost_con_s, 
                            budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement)
        # print(self.qubo_util.show_dict_detail(truck_num_constraint))


    def init_quantum_variables(self):
        self.max_purchases = self.choose_min_purchase()

        excavator_numbers : Dict[str, ndarray] = dict()
        for index, number in enumerate(self.max_purchases):
            if index not in self.excavator_truck_dict.keys():
                continue
            excavator_name = f'excavator{index}'
            excavator_numbers[excavator_name] = self.qubo_util.convert_qubo_ndarray_from_number(number, excavator_name)
        
        used_truck_numbers : Dict[str, ndarray] = dict() # this dictionary refers to common binary variable list in qubo
        half_used_excavator_bits = dict() # this dictionary refers to a binary variable in qubo
        for excavator_index, truck_index in self.excavator_truck_dict.items():
            truck_name = f'truck{truck_index}'
            excavator_name = f'excavator{excavator_index}_half_used'
            used_truck_numbers[truck_name] = self.qubo_util.convert_qubo_ndarray_from_number(self.data.total_truck_numbers[truck_index], truck_name)
            half_used_excavator_bits[excavator_name] = self.qubo_util.convert_qubo_binary(excavator_name)

        # TODO: cost_con_num not initilized, how to calculate?
        one_piece_cost = sum(self.data.excavator_precurement_cost[index] for index in self.excavator_truck_dict.keys())
        cost_con_s = self.qubo_util.convert_qubo_ndarray_from_number(self.data.total_budget - one_piece_cost, 'cost_con_s')
        return excavator_numbers, used_truck_numbers, half_used_excavator_bits, cost_con_s
    
    def choose_min_purchase(self) -> List[int]:
        theatrical_max_purchases = list(make_mapped_generator(self.data.excavator_precurement_cost, lambda cost : self.data.total_budget // cost))
        requested_truck_map = {excavator_index: self.data.total_truck_numbers[truck_index] for excavator_index, truck_index in self.excavator_truck_dict.items() if self.data.excavator_truck_match_dict[excavator_index][truck_index] != 0}
        requested_truck_list = [requested_truck_map.get(excavator_index, 0) for excavator_index in range(self.data.excavator_kinds)]
        return list(min(value1, value2) for value1, value2 in zip(theatrical_max_purchases, requested_truck_list))


    def make_qubo_constraints(self, excavator_numbers : Dict[str, ndarray], fully_used_truck_numbers : Dict[str, ndarray], half_used_excavator_bits: dict, cost_con_s: ndarray):
        cost_generator = (self.data.excavator_precurement_cost[excavator_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}'])
        for excavator_index in self.excavator_truck_dict.keys())
        total_cost = self.qubo_util.kaiwu_sum_proxy(cost_generator)
        cost_con = self.qubo_util.make_qubo_ndarray_sum(cost_con_s)
        
        # Budget constraint
        budget_constraint = self.qubo_util.convert_qubo_constraint(self.data.total_budget - total_cost - cost_con, 'budget')
        truck_num_constraint = {}
        for excavator_index, truck_index in self.excavator_truck_dict.items():
            excavator_name = f'excavator{excavator_index}'
            half_used_excavator_name = f'excavator{excavator_index}_half_used'
            truck_name = f'truck{truck_index}'
            constraint_name = f'excavator{excavator_index}_truck{truck_index}_constraint'
            # if_need_half_used : bool = self.data.excavator_truck_match_dict[excavator_index][truck_index] == 2
            # if if_need_half_used:
            #     constraint_expression = (self.qubo_util.make_qubo_ndarray_sum(fully_used_truck_numbers[truck_name]) + half_used_excavator_bits[half_used_excavator_name] 
            #                 - self.data.excavator_truck_match_dict[excavator_index][truck_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[excavator_name]))
            # else:
            #     constraint_expression = (self.qubo_util.make_qubo_ndarray_sum(fully_used_truck_numbers[truck_name])
            #                 - self.data.excavator_truck_match_dict[excavator_index][truck_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[excavator_name]))
            constraint_expression = (self.qubo_util.make_qubo_ndarray_sum(fully_used_truck_numbers[truck_name]) + half_used_excavator_bits[half_used_excavator_name] 
                            - self.data.excavator_truck_match_dict[excavator_index][truck_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[excavator_name]))
            truck_num_constraint[constraint_name] = self.qubo_util.convert_qubo_constraint(constraint_expression, constraint_name)
        return budget_constraint, truck_num_constraint
    
    def generate_qubo_model(self, excavator_numbers, fully_used_truck_numbers, half_used_excavator_bits, budget_constraint, truck_num_constraint: dict):
        qubo = self.qubo_util
        big_number = 1000000
        
        excavator_produce_efficiency = list(( self.data.excavator_bucket[index] * self.data.excavator_efficiency[index] for index in range(self.data.excavator_kinds)))
        produce_expression_generator = (20 * (excavator_produce_efficiency[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) 
                                              - 0.5 * half_used_excavator_bits[f'excavator{excavator_index}_half_used']) 
                         for excavator_index in self.excavator_truck_dict.keys())
        
        oil_cost_expression_generator = (
            self.data.excavator_oil_consumption[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
                self.data.truck_oil_cosumption[truck_index] * qubo.make_qubo_ndarray_sum(fully_used_truck_numbers[f'truck{truck_index}'])
                for excavator_index, truck_index in self.excavator_truck_dict.items())
        
        labor_maintenance_cost_expression_generator = (
            (self.data.excavator_labor_cost[excavator_index] + self.data.excavator_maintenance_cost[excavator_index]) * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}']) + 
            (self.data.truck_labor_cost[truck_index] + self.data.truck_maintenance_cost[truck_index]) * qubo.make_qubo_ndarray_sum(fully_used_truck_numbers[f'truck{truck_index}']) 
            for excavator_index, truck_index in self.excavator_truck_dict.items())
        
        excavator_precurement_cost_expression_generator = (
            self.data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}'])
            for excavator_index in self.excavator_truck_dict.keys())

        not_need_half_penalty_expression_generator = (half_used_excavator_bits[f'excavator{excavator_index}_half_used'] for excavator_index, truck_index in 
                        self.excavator_truck_dict.items() if self.data.excavator_truck_match_dict[excavator_index][truck_index] == 1)
        
        produce = qubo.kaiwu_sum_proxy(produce_expression_generator)
        oil_consume = qubo.kaiwu_sum_proxy(oil_cost_expression_generator)
        maintenance = qubo.kaiwu_sum_proxy(labor_maintenance_cost_expression_generator)
        precurement = qubo.kaiwu_sum_proxy(excavator_precurement_cost_expression_generator)
        
        total_revenue = 160 * 60 * produce - 160 * 7 * 60 * oil_consume - 60 * maintenance - 10000 * precurement
                    
        object = - total_revenue + big_number / 10 * budget_constraint + qubo.kaiwu_sum_proxy(
            big_number * 50 * truck_num_constraint[f'excavator{excavator_index}_truck{truck_index}_constraint'] 
            for excavator_index, truck_index in self.excavator_truck_dict.items())
        return total_revenue, object, produce, oil_consume, maintenance, precurement
    
    def print_solution(self, obj, total_revenue, excavator_numbers: Dict[str, ndarray], fully_used_truck_numbers: Dict[str, ndarray], half_used_excavator_bits: dict, cost_con_s, 
                       budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement):
        qubo = self.qubo_util
        obj = qubo.qubo_make_proxy(obj)
        obj_ising = qubo.cim_ising_model_proxy(obj)
        matrix = obj_ising.get_ising()["ising"]
        output = qubo.cim_simulator(matrix)
        opt = qubo.optimal_sampler(matrix, output)
        best = opt[0][0]
        cim_best = best * best[-1]
        vars = obj_ising.get_variables()
        sol_dict = qubo.get_sol_dict(cim_best, vars)
       
        obj_val = qubo.get_val(obj, sol_dict)
        total_revenue_val = qubo.get_val(total_revenue, sol_dict)
        budget_constraint_val = qubo.get_val(budget_constraint, sol_dict)
        truck_num_constraint_val = qubo.read_constraint_from_dict(truck_num_constraint, sol_dict)
        excavator_values = qubo.read_nums_from_dict(excavator_numbers, sol_dict)
        truck_values = qubo.read_nums_from_dict(fully_used_truck_numbers, sol_dict)
        half_used_values = qubo.read_bits_from_dict(half_used_excavator_bits, sol_dict)
        cost_con_value = qubo.read_num_from_dict(cost_con_s, sol_dict)
        total_cost = 0
        for excavator_index in self.excavator_truck_dict.keys():
            total_cost += excavator_values[f'excavator{excavator_index}'] * self.data.excavator_precurement_cost[excavator_index]
            
        produce = qubo.get_val(produce, sol_dict)
        oil_consume = qubo.get_val(oil_consume, sol_dict)
        maintenance = qubo.get_val(maintenance, sol_dict)
        precurement = qubo.get_val(precurement, sol_dict)
        
        print(f'total_cost is {total_cost}')
        print(f'cost_con_value is {cost_con_value}')
        print(f'budgt constraint value is {budget_constraint_val}')
        print(f'truck_num_constraint_val is {truck_num_constraint_val}')
        print(f'total_revenue_val is {total_revenue_val}')
        print(f'excavator value is {excavator_values}')
        print(f'truck value is {truck_values}')
        print(f'half_used_values is {half_used_values}')
        print(f'objective value is {obj_val}')
        print(f'produce is {produce * 160 * 60}')
        print(f'oil_consume is {oil_consume * 160 * 7 * 60}')
        print(f'maintenance is {maintenance * 60}')
        print(f'precurement is {precurement * 10000}')
        
        print(f'solution is {sol_dict}')
        # print(half_used_values)
        # print(matrix)