from typing import Generator
from QuboUtil import QuboUtil
from UtilClasses import *
from Instance import Instance
from utils import *

class QuboExprGenerator:
    def __init__(self, qubo_util: QuboUtil, instance: Instance):
        self.qubo_util = qubo_util
        self.instance = instance
        self.data = instance.data
        self.variables = self.__init_qubo_variables()
        
    def get_variables(self) -> Variables:
        return self.variables
        
    def __generate_excavator_max_numbers(self):
        data = self.data
        theatrical_max_purchases = list(
            make_mapped_generator(data.excavator_precurement_cost, lambda cost : ceil(data.total_budget / cost))
        )
        requested_excavator_map = {}
        for excavator_index, matched_truck_numbers in data.excavators_trucks_match_dict.items():
            max_matched_truck_number = [ ceil(max_truck_number / matched_truck_numbers[truck_index]) 
                            for truck_index, max_truck_number in self.instance.truck_number_dict.items() if matched_truck_numbers[truck_index] != 0 ]
            requested_excavator_map[excavator_index] = max(max_matched_truck_number)
                
        requested_excavator_list = [requested_excavator_map.get(excavator_index, 0) for excavator_index in self.instance.excavator_list]
        requested_excavator_purchase_list = [ theatrical_max_purchases[excavator_index] for excavator_index in self.instance.excavator_list ]
        final_excavator_list = list(min(value1, value2) for value1, value2 in zip(requested_excavator_list, requested_excavator_purchase_list))
        return {excavator_index : final_excavator_list[index] for index, excavator_index in enumerate(self.instance.excavator_list)}

    
    def __init_qubo_variables(self):
        qubo = self.qubo_util
        instance = self.instance
        et_match_dict = self.data.excavators_trucks_match_dict
        
        cost_constraint_num = qubo.generate_qubo_ndarray_from_number(self.data.total_budget, 'cost_constraint')
        
        excavator_number_dict = self.__generate_excavator_max_numbers()
        excavator_number_qubo_dict = {excavator_index : qubo.generate_qubo_ndarray_from_number(max_number, f'excavator_{excavator_index}') 
                                      for excavator_index, max_number in excavator_number_dict.items()}
        excavator_truck_match_qubo_binary_dict = {(excavator_index, truck_index) : qubo.generate_qubo_binary(f'excavator_{excavator_index}_truck_{truck_index}') 
                                                  for excavator_index in instance.excavator_list for truck_index in instance.truck_list 
                                                   if et_match_dict[excavator_index][truck_index] != 0 }
        excavator_half_use_qubo_binary_dict = {(excavator_index, truck_index): qubo.generate_qubo_binary(f'excavator_{excavator_index}_half_use_truck_{truck_index}') 
                                               for excavator_index in instance.excavator_list for truck_index in instance.truck_list 
                                               if et_match_dict[excavator_index][truck_index] != 0 }
        
        # Here we use other info to cal the truck number qubo dict
        truck_number_qubo_dict = { truck_index: self.qubo_util.kaiwu_sum_proxy(
                  excavator_truck_match_qubo_binary_dict[(excavator_index, truck_index)] * excavator_number_qubo_dict[excavator_index]
                  * self.data.excavators_trucks_match_dict[excavator_index][truck_index] - excavator_half_use_qubo_binary_dict[(excavator_index, truck_index)] 
                  for excavator_index in self.instance.excavator_list) for truck_index in instance.truck_list }
        return Variables(cost_constraint_num, 
                         excavator_number_qubo_dict, 
                         truck_number_qubo_dict, 
                         excavator_truck_match_qubo_binary_dict, 
                         excavator_half_use_qubo_binary_dict)
        
    def excavator_purchase_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.excavator_precurement_cost[excavator_index] * qubo.make_qubo_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) 
                for excavator_index in self.instance.excavator_list)
    
    def excavator_oil_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.oil_price * data.excavator_oil_consumption[excavator_index] * qubo.make_qubo_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index])
                for excavator_index in self.instance.excavator_list)
    
    def truck_oil_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.oil_price * data.truck_oil_consumption[truck_index] * qubo.make_qubo_ndarray_sum(self.variables.truck_number_qubo_dict[truck_index])
                for truck_index in self.instance.truck_list)
    
    def excavator_maintenance_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.excavator_maintenance_cost[excavator_index] * qubo.make_qubo_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index])
                for excavator_index in self.instance.excavator_list)
    
    def truck_maintenance_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.truck_maintenance_cost[truck_index] * qubo.make_qubo_ndarray_sum(self.variables.truck_number_qubo_dict[truck_index])
                for truck_index in self.instance.truck_list)
        
    def produce_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.workdays_per_month * data.excavator_produce_efficiency[excavator_index] * 
                (qubo.make_qubo_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) - 0.5 * 
                 self.variables.excavator_half_use_qubo_binary_dict[(excavator_index, truck_index)])
                for excavator_index in self.instance.excavator_list for truck_index in self.instance.truck_list)
        
    def total_revenue(self, produce, oil_consumption_cost, maintenance_cost, precurement_cost):
        return 160 * 60 * produce - 160 * 60 * oil_consumption_cost - 60 * maintenance_cost - 10000 * precurement_cost