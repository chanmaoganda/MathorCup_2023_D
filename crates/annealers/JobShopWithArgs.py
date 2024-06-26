import os
from typing import Dict

from numpy import ndarray, single
from DataStorage import DataStorage
from GeneratorConstraintHandler import GeneratorConstraintHandler
from Object import Object
from QuboUtil import QuboUtil
from Solution import Solution
from Instance import Instance
from util_class import Constraints
from util_class import Variables
from utils import *
import json

class JobShopWithArgs:
    
    def __init__(self, instance: Instance):
        self.truck_number_dict: Dict[int, int] = instance.truck_number_dict
        self.data = instance.data
        self.sequence_number = instance.iteration

        self.excavator_list = instance.excavator_list
        self.truck_list = instance.truck_list

        self.qubo_util = QuboUtil()
        self.generator_constraint_handler = GeneratorConstraintHandler(self.qubo_util, instance)
        self.best_solution = {0 : 7, 1 : 7, 3: 2}
    
    def gen_output_dir(self) -> str:
        parent_dir = '/home/avania/projects/python/MathorCupD-2023/data'
        excavators = self.excavator_truck_dict.keys()
        directory = f'{excavators[0]}-{excavators[1]}-{excavators[2]}'
        return os.path.join(parent_dir, directory)
        
    def solve(self):
        variables = self.init_quantum_variables()
        constraints = self.make_qubo_constraints(variables)
        excavator_numbers, truck_numbers, excavator_truck_usage, half_used_excavator_bits, cost_con_s = variables.unpack_variables()
        budget_constraint, truck_num_constraint, excavator_single_match_constraint, truck_single_match_constraint = constraints.unpack_constraints()
        total_revenue, object, produce, oil_consume, maintenance, precurement = self.generate_qubo_model(variables, constraints)
        self.solution = Solution(object, total_revenue, excavator_numbers, truck_numbers, half_used_excavator_bits, cost_con_s, budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement)
        self.solved_results, self.obj_ising = self.get_solved_cim_results(self.solution)
        
        output_dir = self.gen_output_dir()
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        print(output_dir)
        self.dir_path = os.path.join(output_dir, f'iteration-{self.sequence_number}')
        print(self.dir_path)
        self.path_exists = os.path.exists(self.dir_path)
        
        for index in range(30):
            self.write_solution(index)

    def init_quantum_variables(self) -> Variables:
        max_purchases = self.choose_min_purchase()
        excavator_numbers : Dict[str, ndarray] = dict()
        for excavator_index, max_purchase_number in max_purchases.items():
            excavator_name = f'excavator{excavator_index}'
            excavator_numbers[excavator_name] = self.qubo_util.generate_qubo_ndarray_from_number(max_purchase_number, excavator_name)
        
        used_truck_numbers : Dict[str, ndarray] = dict() # this dictionary refers to common binary variable list in qubo
        half_used_excavator_bits = dict() # this dictionary refers to a variable in qubo
        
        for excavator_index, truck_index in self.excavator_truck_dict.items():
            truck_name = f'truck{truck_index}'
            excavator_name = f'excavator{excavator_index}_half_used'
            used_truck_numbers[truck_name] = self.qubo_util.generate_qubo_ndarray_from_number(self.data.total_truck_numbers[truck_index], truck_name)
            half_used_excavator_bits[excavator_name] = self.qubo_util.generate_qubo_binary(excavator_name)
        
        excavator_truck_usage = { f'excavator{excavator_index}_truck{truck_index}_usage' : 
                                    self.qubo_util.generate_qubo_binary(f'excavator_{excavator_index}_truck_{truck_index}_usage') 
                    for excavator_index in self.excavator_truck_dict.keys() for truck_index in self.excavator_truck_dict.values()
                        if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0}

        one_piece_cost = sum(self.data.excavator_precurement_cost[index] for index in self.excavator_list)
        cost_con_s = self.qubo_util.generate_qubo_ndarray_from_number(self.data.total_budget - one_piece_cost, 'cost_con_s')
        return Variables(excavator_numbers, used_truck_numbers, excavator_truck_usage, half_used_excavator_bits, cost_con_s)
    
    def choose_min_purchase(self) -> Dict[int, int]:
        data = self.data
        theatrical_max_purchases = list(
            make_mapped_generator(data.excavator_precurement_cost, lambda cost : ceil(data.total_budget // cost))
        )
        requested_excavator_map = {}
        for excavator_index, matched_truck_numbers in data.excavators_trucks_match_dict.items():
            max_matched_truck_number = [ ceil(max_truck_number / matched_truck_numbers[truck_index]) 
                            for truck_index, max_truck_number in self.truck_number_dict.items() if matched_truck_numbers[truck_index] != 0 ]
            requested_excavator_map[excavator_index] = max(max_matched_truck_number)
                
        requested_excavator_list = [requested_excavator_map.get(excavator_index, 0) for excavator_index in self.excavator_list]
        requested_excavator_purchase_list = [ theatrical_max_purchases[excavator_index] for excavator_index in self.excavator_list ]
        final_excavator_list = list(min(value1, value2) for value1, value2 in zip(requested_excavator_list, requested_excavator_purchase_list))
        return {excavator_index : final_excavator_list[index] for index, excavator_index in enumerate(self.excavator_list)}


    def make_qubo_constraints(self, variables: Variables) -> Constraints:
        qubo = self.qubo_util
        excavator_numbers, truck_numbers, excavator_truck_usage, half_used_excavator_bits, cost_con_s = variables.unpack_variables()
        cost_generator = (self.data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[f'excavator{excavator_index}'])
                for excavator_index in self.excavator_truck_dict.keys())
        total_cost = qubo.kaiwu_sum_proxy(cost_generator)
        cost_con = qubo.make_qubo_ndarray_sum(cost_con_s)
        
        # Budget constraint
        budget_constraint = qubo.generate_qubo_constraint(self.data.total_budget - total_cost - cost_con, 'budget')
        truck_num_constraint = {}
        excavator_single_match_constraint = {}
        truck_single_match_constraint = {}
        
        for excavator_index in self.excavator_truck_dict.keys():
            constraint_expression = (qubo.kaiwu_sum_proxy(
                (excavator_truck_usage[f'excavator_{excavator_index}_truck_{truck_index}'] 
                    for truck_index in self.excavator_truck_dict.values() 
                        if f'excavator_{excavator_index}_truck_{truck_index}_usage' in excavator_truck_usage.keys() )
                ))
            
            excavator_single_match_constraint[f'excavator{excavator_index}_single_match_constraint'] = qubo.generate_qubo_constraint(
                constraint_expression, f'excavator{excavator_index}_single_match_constraint'
                )
            
        for truck_index in self.excavator_truck_dict.values():
            constraint_expression = (qubo.kaiwu_sum_proxy(
                (excavator_truck_usage[f'excavator_{excavator_index}_truck_{truck_index}'] 
                    for excavator_index in self.excavator_truck_dict.keys()
                     if f'excavator_{excavator_index}_truck_{truck_index}_usage' in excavator_truck_usage.keys() )
                ))
            
            truck_single_match_constraint[f'truck{truck_index}_single_match_constraint'] = qubo.generate_qubo_constraint(
                constraint_expression, f'truck{truck_index}_single_match_constraint'
                )
            
        for excavator_index, truck_index in self.excavator_truck_dict.items():
            excavator_name = f'excavator{excavator_index}'
            half_used_excavator_name = f'excavator{excavator_index}_half_used'
            truck_name = f'truck{truck_index}'
            constraint_name = f'excavator{excavator_index}_truck{truck_index}_constraint'
            constraint_expression = (qubo.make_qubo_ndarray_sum(truck_numbers[truck_name]) + half_used_excavator_bits[half_used_excavator_name] 
                - self.data.excavators_trucks_match_dict[excavator_index][truck_index] * qubo.make_qubo_ndarray_sum(excavator_numbers[excavator_name]))
            truck_num_constraint[constraint_name] = qubo.generate_qubo_constraint(constraint_expression, constraint_name)
            
        constraints = Constraints(budget_constraint, truck_num_constraint, excavator_single_match_constraint, truck_single_match_constraint)
        return constraints
    
    def generate_qubo_model(self, variables: Variables, constraints: Constraints):
        qubo = self.qubo_util
        excavator_numbers, truck_numbers, _, half_used_excavator_bits, _ = variables.unpack_variables()
        budget_constraint, truck_num_constraint, excavator_single_match_constraint, truck_single_match_constraint = constraints.unpack_constraints()
        
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
                    
        object = handler.object_expression_factory(total_revenue, budget_constraint, excavator_single_match_constraint, truck_single_match_constraint)
        
        return total_revenue, object, produce, oil_consume, maintenance_cost, precurement_cost
        
    def calculate_theoretical_cost(self, excavator_numbers: Dict[int, float], truck_numbers: Dict[int, float], half_used_excavator_bits: Dict[int, float],
                                   cost_con_val):
        data = self.data
        qubo = self.qubo_util
        handler = self.generator_constraint_handler
        produce = sum(handler.excavator_produce_expression_factory(excavator_numbers, half_used_excavator_bits))
        oil_consume = sum(handler.oil_cost_expression_factory(excavator_numbers, truck_numbers))
        maintenance_cost = sum(handler.labor_maintenance_cost_expression_factory(excavator_numbers, truck_numbers))
        precurement_cost = sum(handler.excavator_precurement_cost_expression_factory(excavator_numbers))
        total_revenue = handler.total_revenue_expression_factory(produce, oil_consume, maintenance_cost, precurement_cost)
        
        excavator_produce_dict: Dict[int, float] = {}
        for excavator_index in self.excavator_truck_dict.keys():
            current_produce = (excavator_numbers[excavator_index] - 0.5 * half_used_excavator_bits[excavator_index]) * 20 * data.excavator_produce_efficiency[excavator_index]
            excavator_produce_dict[excavator_index] = current_produce

        budget_constraint = (data.total_budget - cost_con_val - precurement_cost) ** 2
        truck_num_constraint = {excavator_index : truck_numbers[truck_index] + half_used_excavator_bits[excavator_index]
            - data.excavators_trucks_match_dict[excavator_index][truck_index] * excavator_numbers[excavator_index] for excavator_index, truck_index in self.excavator_truck_dict.items()}
        # TODO
        # object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)
        
        half_used_excavator_values_dict = {}
        for excavator_index, constraint_value in truck_num_constraint.items():
            value = constraint_value ** 2
            half_used_excavator_values_dict[excavator_index] = value
        # TODO
        # object = handler.object_expression_factory(total_revenue, budget_constraint, truck_num_constraint)

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
        with open(f'{self.dir_path}/{opt_sequence}-solution.json', 'w') as file:
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