from numpy import ndarray

from utils import *
from typing import Dict
from Instance import Instance
from UtilClasses import *
from QuboUtil import QuboUtil
from UtilClasses import Variables


class SubQuboSolver:
    data: DataStorage
    def __init__(self, instance: Instance):
        self.truck_number_dict: Dict[int, int] = instance.truck_number_dict
        self.data = instance.data
        self.sequence_number = instance.iteration

        self.excavator_list = instance.excavator_list
        self.truck_list = instance.truck_list

        self.qubo_util = QuboUtil()
        
    def __generate_excavator_max_numbers(self):
        data = self.data
        theatrical_max_purchases = list(
            make_mapped_generator(data.excavator_precurement_cost, lambda cost : ceil(data.total_budget / cost))
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
        
    def init_qubo_variables(self):
        qubo = self.qubo_util
        et_match_dict = self.data.excavators_trucks_match_dict
        
        cost_constraint_num = qubo.generate_qubo_ndarray_from_number(self.data.total_budget, 'cost_constraint')
        
        excavator_number_dict = self.__generate_excavator_max_numbers()
        excavator_number_qubo_dict = {excavator_index : qubo.generate_qubo_ndarray_from_number(max_number, f'excavator_{excavator_index}') 
                                      for excavator_index, max_number in excavator_number_dict.items()}
        truck_number_qubo_dict = {truck_index : qubo.generate_qubo_ndarray_from_number(max_number, f'truck_{truck_index}') 
                                  for truck_index, max_number in self.truck_number_dict.items()} 
        excavator_truck_match_qubo_binary_dict = {(excavator_index, truck_index) : qubo.generate_qubo_binary(f'excavator_{excavator_index}_truck_{truck_index}') 
                                                  for excavator_index in self.excavator_list for truck_index in self.truck_list 
                                                   if et_match_dict[excavator_index][truck_index] != 0 }
        excavator_half_use_qubo_binary_dict = {(excavator_index, truck_index): qubo.generate_qubo_binary(f'excavator_{excavator_index}_half_use_truck_{truck_index}') 
                                               for excavator_index in self.excavator_list for truck_index in self.truck_list 
                                               if et_match_dict[excavator_index][truck_index] != 0 }
        return Variables(cost_constraint_num, 
                         excavator_number_qubo_dict, 
                         truck_number_qubo_dict, 
                         excavator_truck_match_qubo_binary_dict, 
                         excavator_half_use_qubo_binary_dict)

    def generate_qubo_constraints(self, variables: Variables):
        qubo = self.qubo_util
        data = self.data
        
        