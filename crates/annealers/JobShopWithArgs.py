import os
from typing import Dict

from numpy import ndarray
from DataStorage import DataStorage
from GeneratorConstraintHandler import GeneratorConstraintHandler
from Object import Object
from QuboUtil import QuboUtil
from Solution import Solution
from InstanceSolver import InstanceSolver
from utils import *
import json

class JobShopWithArgs:
    def __init__(self, instance_solver: InstanceSolver):

        self.excavator_truck_dict: Dict[int, int] = { excavator: truck for excavator, truck in 
                            zip(instance_solver.excavator_list, instance_solver.truck_list) }
        self.data = instance_solver.data
        self.sequence_number = instance_solver.iteration
        self.qubo_util = QuboUtil()
        self.generator_constraint_handler = GeneratorConstraintHandler(self.qubo_util, self.data, self.excavator_truck_dict)
        self.best_solution = {0 : 7, 1 : 7, 3: 2}
        
        
    def solve(self):
        excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s = self.init_quantum_variables()
        budget_constraint, truck_num_constraint = self.make_qubo_constraints(excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s)

        total_revenue, object, produce, oil_consume, maintenance, precurement = self.generate_qubo_model(excavator_numbers, truck_numbers, half_used_excavator_bits, budget_constraint, truck_num_constraint)
        self.solution = Solution(object, total_revenue, excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s, budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement)
        self.solved_results, self.obj_ising = self.get_solved_cim_results(self.solution)

        parent_dir = '/home/avania/projects/python/MathorCupD-2023/data'
        directory = f'iteration-{self.sequence_number}'
        self.dir_path = os.path.join(parent_dir, directory)
        self.path_exists = os.path.exists(self.dir_path)
        
        for index in range(10):
            self.write_solution(index)

    def init_quantum_variables(self):
        self.max_purchases = self.choose_min_purchase()

        excavator_numbers : Dict[str, ndarray] = dict()
        for index, number in enumerate(self.max_purchases):
            if index not in self.excavator_truck_dict.keys():
                continue
            excavator_name = f'excavator{index}'
            excavator_numbers[excavator_name] = self.qubo_util.convert_qubo_ndarray_from_number(number, excavator_name)
        
        used_truck_numbers : Dict[str, ndarray] = dict() # this dictionary refers to common binary variable list in qubo
        half_used_excavator_bits = dict() # this dictionary refers to a variable in qubo
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
        requested_truck_map = {excavator_index: self.data.total_truck_numbers[truck_index] for excavator_index, truck_index in self.excavator_truck_dict.items() if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0}
        requested_truck_list = [requested_truck_map.get(excavator_index, 0) for excavator_index in range(self.data.excavator_kinds)]
        return list(min(value1, value2) for value1, value2 in zip(theatrical_max_purchases, requested_truck_list))


    def make_qubo_constraints(self, excavator_numbers : Dict[str, ndarray], truck_numbers : Dict[str, ndarray], half_used_excavator_bits: dict, cost_con_s: ndarray):
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
        for excavator_index in self.excavator_truck_dict.keys():
            current_produce = (excavator_numbers[excavator_index] - 0.5 * half_used_excavator_bits[excavator_index]) * 20 * data.excavator_produce_efficiency[excavator_index]
            excavator_produce_dict[excavator_index] = current_produce

        budget_constraint = (data.total_budget - cost_con_val - precurement_cost) ** 2
        truck_num_constraint = {excavator_index : truck_numbers[truck_index] + half_used_excavator_bits[excavator_index]
            - data.excavators_trucks_match_dict[excavator_index][truck_index] * excavator_numbers[excavator_index] for excavator_index, truck_index in self.excavator_truck_dict.items()}
        object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)
        
        half_used_excavator_values_dict = {}
        for excavator_index, constraint_value in truck_num_constraint.items():
            value = constraint_value ** 2
            half_used_excavator_values_dict[excavator_index] = value
        object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)

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
        for excavator_index in self.excavator_truck_dict.keys():
            total_cost += excavator_values[f'excavator{excavator_index}'] * self.data.excavator_precurement_cost[excavator_index]
            
        produce_cost = qubo.get_val(solution.produce, sol_dict)
        oil_consume_cost = qubo.get_val(solution.oil_consume, sol_dict)
        maintenance_cost = qubo.get_val(solution.maintenance, sol_dict)
        precurement_cost = qubo.get_val(solution.precurement, sol_dict)
        excavator_produce_dict = {excavator_index : 
            qubo.get_val(20 * data.excavator_produce_efficiency[excavator_index] * (qubo.make_qubo_ndarray_sum(solution.excavator_numbers[f'excavator{excavator_index}']) 
                                              - 0.5 * solution.half_used_excavator_bits[f'excavator{excavator_index}_half_used']), sol_dict)
                         for excavator_index in self.excavator_truck_dict.keys()}

        # if excavator_values.values() != [7.0, 7.0, 2.0]:
        #     return
        if not self.path_exists :
            os.mkdir(self.dir_path)
            # print(f'directory {self.dir_path} created')
            self.path_exists = True
        object_json = Object(total_cost, cost_con_value, budget_constraint_val, truck_num_constraint_val, excavator_values, truck_values, half_used_values, total_revenue_val, obj_val, produce_cost, oil_consume_cost, maintenance_cost, precurement_cost, excavator_produce_dict)
        with open(f'/home/avania/projects/python/MathorCupD-2023/data/iteration-{self.sequence_number}/{opt_sequence}-solution.json', 'w') as file:
            # print(f'writing solution to file {self.dir_path}/{opt_sequence}-solution.json')
            file.write(json.dumps(object_json.__dict__))
    
    def make_all_instances(self) -> List[List[int]]:
        match_dict = self.data.excavators_trucks_match_dict

        matches = self.__find_matches(0, [key for key in match_dict.keys()])
        for match in matches:
            match.reverse()

        return matches

    
    def __find_matches(self, epoch: int, current_sequence: List[int]) -> List[List[int]]:
        truck_kinds = self.data.truck_kinds
        match_dict = self.data.excavators_trucks_match_dict
        
        if epoch == truck_kinds - 1:
            return [[excavator_index] for excavator_index in current_sequence if match_dict[excavator_index][epoch] != 0]
        result = []
        for index in range(len(current_sequence)):
            excavator = current_sequence.pop(0)
            if match_dict[excavator][epoch] == 0:
                current_sequence.append(excavator)
                continue
            matches = self.__find_matches(epoch + 1, current_sequence)

            for match in matches:
                match.append(excavator)
            current_sequence.append(excavator)
            result.extend(matches)
        return result