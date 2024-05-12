import os
from typing import Dict

from numpy import ndarray
from DataStorage import DataStorage
from GeneratorConstraintHandler import GeneratorConstraintHandler
from Object import Object
from QuboUtil import QuboUtil
from Solution import Solution
from utils import *
import json
from multiprocessing import Pool


class JobShopWithArgs:
    def __init__(self, excavators: list, trucks: list, sequence_number = 0):
        excavator_truck_dict: Dict[int, int] = { excavator: truck for excavator, truck in zip(excavators, trucks)}
        self.data = DataStorage(total_budget = 2400, excavator_truck_dict = excavator_truck_dict, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                                excavator_oil_consumption = [28,30,34,38], truck_oil_cosumption = [18, 22, 27],
                                excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                                excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                                excavator_precurement_cost = [100, 140, 300, 320], 
                                excavators_trucks_match_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]},
                                total_truck_numbers = [7, 7, 3])
        self.sequence_number = sequence_number
        self.qubo_util = QuboUtil()
        self.generator_constraint_handler = GeneratorConstraintHandler(self.qubo_util, self.data)
        self.best_solution = {0 : 7, 1 : 7, 3: 2}
        
        
    def solve(self):
        excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s = self.init_quantum_variables()
        # print(f'current used bits are {self.qubo_util.total_bits}')
        budget_constraint, truck_num_constraint = self.make_qubo_constraints(excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s)

        total_revenue, object, produce, oil_consume, maintenance, precurement = self.generate_qubo_model(excavator_numbers, truck_numbers, half_used_excavator_bits, budget_constraint, truck_num_constraint)
        self.solution = Solution(object, total_revenue, excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s, budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement)
        self.solved_results, self.obj_ising = self.get_solved_cim_results(self.solution)

        parent_dir = '/home/avania/projects/python/qboson/JobShopScheduling/data'
        directory = f'iteration-{self.sequence_number}'
        self.dir_path = os.path.join(parent_dir, directory)
        self.path_exists = os.path.exists(self.dir_path)
            
        for index in range(100):
            self.write_solution(index)

    def init_quantum_variables(self):
        self.max_purchases = self.choose_min_purchase()

        excavator_numbers : Dict[str, ndarray] = dict()
        for index, number in enumerate(self.max_purchases):
            if index not in self.data.excavator_truck_dict.keys():
                continue
            excavator_name = f'excavator{index}'
            excavator_numbers[excavator_name] = self.qubo_util.convert_qubo_ndarray_from_number(number, excavator_name)
        
        used_truck_numbers : Dict[str, ndarray] = dict() # this dictionary refers to common binary variable list in qubo
        half_used_excavator_bits = dict() # this dictionary refers to a variable in qubo
        for excavator_index, truck_index in self.data.excavator_truck_dict.items():
            truck_name = f'truck{truck_index}'
            excavator_name = f'excavator{excavator_index}_half_used'
            used_truck_numbers[truck_name] = self.qubo_util.convert_qubo_ndarray_from_number(self.data.total_truck_numbers[truck_index], truck_name)
            half_used_excavator_bits[excavator_name] = self.qubo_util.convert_qubo_binary(excavator_name)

        # TODO: cost_con_num not initilized, how to calculate?
        one_piece_cost = sum(self.data.excavator_precurement_cost[index] for index in self.data.excavator_truck_dict.keys())
        cost_con_s = self.qubo_util.convert_qubo_ndarray_from_number(self.data.total_budget - one_piece_cost, 'cost_con_s')
        return excavator_numbers, used_truck_numbers, half_used_excavator_bits, cost_con_s
    
    def choose_min_purchase(self) -> List[int]:
        theatrical_max_purchases = list(make_mapped_generator(self.data.excavator_precurement_cost, lambda cost : self.data.total_budget // cost))
        requested_truck_map = {excavator_index: self.data.total_truck_numbers[truck_index] for excavator_index, truck_index in self.data.excavator_truck_dict.items() if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0}
        requested_truck_list = [requested_truck_map.get(excavator_index, 0) for excavator_index in range(self.data.excavator_kinds)]
        return list(min(value1, value2) for value1, value2 in zip(theatrical_max_purchases, requested_truck_list))


    def make_qubo_constraints(self, excavator_numbers : Dict[str, ndarray], truck_numbers : Dict[str, ndarray], half_used_excavator_bits: dict, cost_con_s: ndarray):
        cost_generator = (self.data.excavator_precurement_cost[excavator_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}'])
        for excavator_index in self.data.excavator_truck_dict.keys())
        total_cost = self.qubo_util.kaiwu_sum_proxy(cost_generator)
        cost_con = self.qubo_util.make_qubo_ndarray_sum(cost_con_s)
        
        # Budget constraint
        budget_constraint = self.qubo_util.convert_qubo_constraint(self.data.total_budget - total_cost - cost_con, 'budget')
        truck_num_constraint = {}
        for excavator_index, truck_index in self.data.excavator_truck_dict.items():
            excavator_name = f'excavator{excavator_index}'
            half_used_excavator_name = f'excavator{excavator_index}_half_used'
            truck_name = f'truck{truck_index}'
            constraint_name = f'excavator{excavator_index}_truck{truck_index}_constraint'
            constraint_expression = (self.qubo_util.make_qubo_ndarray_sum(truck_numbers[truck_name]) + half_used_excavator_bits[half_used_excavator_name] 
                - self.data.excavators_trucks_match_dict[excavator_index][truck_index] * self.qubo_util.make_qubo_ndarray_sum(excavator_numbers[excavator_name]))
            truck_num_constraint[constraint_name] = self.qubo_util.convert_qubo_constraint(constraint_expression, constraint_name)
        return budget_constraint, truck_num_constraint
    
    def generate_qubo_model(self, excavator_numbers: Dict[str, ndarray], truck_numbers: Dict[str, ndarray], 
                            half_used_excavator_bits: dict, budget_constraint, truck_num_constraint: dict):
        qubo = self.qubo_util
        handler = self.generator_constraint_handler
        
        produce_expression_generator = handler.excavator_produce_expression_factory(excavator_numbers, half_used_excavator_bits)
        oil_cost_expression_generator = handler.oil_cost_expression_factory(excavator_numbers, truck_numbers)
        labor_maintenance_cost_expression_generator = handler.labor_maintenance_cost_expression_factory(excavator_numbers, truck_numbers)
        excavator_precurement_cost_expression_generator = handler.excavator_precurement_cost_expression_factory(excavator_numbers)
        
        produce = qubo.kaiwu_sum_proxy(produce_expression_generator)
        oil_consume = qubo.kaiwu_sum_proxy(oil_cost_expression_generator)
        maintenance_cost = qubo.kaiwu_sum_proxy(labor_maintenance_cost_expression_generator)
        precurement_cost = qubo.kaiwu_sum_proxy(excavator_precurement_cost_expression_generator)
        
        total_revenue = handler.total_revenue_expression_factory(produce, oil_consume, maintenance_cost, precurement_cost)
                    
        object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)
        
        return total_revenue, object, produce, oil_consume, maintenance_cost, precurement_cost
        
    def calculate_theoretical_cost(self, excavator_numbers: Dict[int, float], truck_numbers: Dict[int, float], half_used_excavator_bits: Dict[int, float],
                                   cost_con_val):
        data = self.data
        qubo = self.qubo_util
        handler = self.generator_constraint_handler
        produce = sum(handler.excavator_produce_expression_factory(excavator_numbers, half_used_excavator_bits))
        oil_consume = sum(handler.oil_cost_expression_factory(excavator_numbers, truck_numbers))
        mainteinance_cost = sum(handler.labor_maintenance_cost_expression_factory(excavator_numbers, truck_numbers))
        precurement_cost = sum(handler.excavator_precurement_cost_expression_factory(excavator_numbers))
        total_revenue = handler.total_revenue_expression_factory(produce, oil_consume, mainteinance_cost, precurement_cost)
        
        excavator_produce_dict: Dict[int, float] = {}
        for excavator_index in self.data.excavator_truck_dict.keys():
            current_produce = (excavator_numbers[excavator_index] - 0.5 * half_used_excavator_bits[excavator_index]) * 20 * data.excavator_produce_efficiency[excavator_index]
            excavator_produce_dict[excavator_index] = current_produce

        budget_constraint = (data.total_budget - cost_con_val - precurement_cost) ** 2
        truck_num_constraint = {excavator_index : truck_numbers[truck_index] + half_used_excavator_bits[excavator_index]
            - data.excavators_trucks_match_dict[excavator_index][truck_index] * excavator_numbers[excavator_index] for excavator_index, truck_index in self.data.excavator_truck_dict.items()}
        object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)
        
        half_used_excavator_values_dict = {}
        for excavator_index, constraint_value in truck_num_constraint.items():
            value = constraint_value ** 2
            half_used_excavator_values_dict[excavator_index] = value
        object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)
        
        
        # print(f'budget_val is {budget_constraint}')
        # print(f'total_revenue_val is {total_revenue}')
        # print(f'objective value is {object}')
        # print(f'produce is {produce}')
        # print(f'oil_consume is {oil_consume}')
        # print(f'mainteinance_cost is {mainteinance_cost}')
        # print(f'precurement_cost is {precurement_cost}')
        # print(f'excavator_produce_dict is {excavator_produce_dict}')
        # print(f'half_used_excavator_values_dict is {half_used_excavator_values_dict}')
    def get_solved_cim_results(self, solution: Solution): 
        qubo = self.qubo_util
        
        obj = qubo.qubo_make_proxy(solution.obj)
        obj_ising = qubo.cim_ising_model_proxy(obj)
        matrix = obj_ising.get_ising()["ising"]
        output = qubo.cim_simulator(matrix)
        opt = qubo.optimal_sampler(matrix, output)
        return opt[0], obj_ising
        
    def write_solution(self, opt_sequence : int):
        qubo = self.qubo_util
        data = self.data
        solution = self.solution

        best = self.solved_results[opt_sequence]
        cim_best = best * best[-1]
        vars = self.obj_ising.get_variables()
        sol_dict = qubo.get_sol_dict(cim_best, vars)
       
        obj_val = qubo.get_val(solution.obj, sol_dict)
        excavator_values = qubo.read_nums_from_dict(solution.excavator_numbers, sol_dict)
        
        total_revenue_val = qubo.get_val(solution.total_revenue, sol_dict)
        budget_constraint_val = qubo.get_val(solution.budget_constraint, sol_dict)
        truck_num_constraint_val = qubo.read_constraint_from_dict(solution.truck_num_constraint, sol_dict)
        truck_values = qubo.read_nums_from_dict(solution.truck_numbers, sol_dict)
        half_used_values = qubo.read_bits_from_dict(solution.half_used_excavator_bits, sol_dict)
        cost_con_value = qubo.read_num_from_dict(solution.cost_con_s, sol_dict)
        total_cost = 0
        for excavator_index in self.data.excavator_truck_dict.keys():
            total_cost += excavator_values[f'excavator{excavator_index}'] * self.data.excavator_precurement_cost[excavator_index]
            
        produce_cost = qubo.get_val(solution.produce, sol_dict)
        oil_consume_cost = qubo.get_val(solution.oil_consume, sol_dict)
        maintenance_cost = qubo.get_val(solution.maintenance, sol_dict)
        precurement_cost = qubo.get_val(solution.precurement, sol_dict)
        excavator_produce_dict = {excavator_index : 
            qubo.get_val(20 * data.excavator_produce_efficiency[excavator_index] * (qubo.make_qubo_ndarray_sum(solution.excavator_numbers[f'excavator{excavator_index}']) 
                                              - 0.5 * solution.half_used_excavator_bits[f'excavator{excavator_index}_half_used']), sol_dict)
                         for excavator_index in self.data.excavator_truck_dict.keys()}

        if excavator_values.values() != [7.0, 7.0, 2.0]:
            return
        if not self.path_exists :
            os.mkdir(self.dir_path)
            self.path_exists = True
        object_json = Object(total_cost, cost_con_value, budget_constraint_val, truck_num_constraint_val, excavator_values, truck_values, half_used_values, total_revenue_val, obj_val, produce_cost, oil_consume_cost, maintenance_cost, precurement_cost, excavator_produce_dict)
        with open(f'/home/avania/projects/python/qboson/JobShopScheduling/data/iteration-{self.sequence_number}/{opt_sequence}-solution.json', 'w') as file:
            file.write(json.dumps(object_json.__dict__))

        # if excavator_values.values() == [7, 7, 2]:
        # print(f'The solution is {excavator_values},\n truck is {truck_values},\n half use is {half_used_values},\n total revenue is {total_revenue_val}\n')

        # print(f'total_cost is {total_cost}')
        # print(f'cost_con_value is {cost_con_value}')
        # print(f'budgt constraint value is {budget_constraint_val}')
        # print(f'truck_num_constraint_val is {truck_num_constraint_val}')
        # print(f'excavator value is {excavator_values}')
        # print(f'truck value is {truck_values}')
        # print(f'half_used_values is {half_used_values}')
        # print(f'total_revenue_val is {total_revenue_val}')
        # print(f'objective value is {obj_val}')
        # print(f'produce is {produce_cost}')
        # print(f'oil_consume is {oil_consume_cost}')
        # print(f'maintenance_cost is {maintenance_cost}')
        # print(f'precurement_cost is {precurement_cost}')
        # print(f'excavator_produce_dict is {excavator_produce_dict}')
        # print("")
        
        # # test parts
        # excavator_dict: Dict[int, float] = dict()
        # for excavator_index in self.data.excavator_truck_dict.keys():
        #     excavator_dict[excavator_index] = excavator_values[f'excavator{excavator_index}']

        # truck_dict: Dict[int, float] = dict()
        # for truck_index in self.data.excavator_truck_dict.values():
        #     truck_dict[truck_index] = truck_values[f'truck{truck_index}']
        
        # half_used_dict: Dict[int, float] = dict()
        # for excavator_index in self.data.excavator_truck_dict.keys():
        #     half_used_dict[excavator_index] = half_used_values[f'excavator{excavator_index}_half_used']
            
        # self.calculate_theoretical_cost(excavator_dict, truck_dict, half_used_dict, cost_con_value)
        