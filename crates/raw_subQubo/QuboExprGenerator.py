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
        
        cost_constraint_num = qubo.ndarray_from_number(self.data.total_budget, 'cost_constraint')
        
        excavator_number_dict = self.__generate_excavator_max_numbers()
        excavator_number_qubo_dict = {excavator_index : qubo.ndarray_from_number(max_number, f'excavator_{excavator_index}') 
                                      for excavator_index, max_number in excavator_number_dict.items()}
        excavator_truck_match_qubo_binary_dict = {(excavator_index, truck_index) : qubo.generate_qubo_binary(f'excavator_{excavator_index}_truck_{truck_index}') 
                                                  for excavator_index in instance.excavator_list for truck_index in instance.truck_list 
                                                   if et_match_dict[excavator_index][truck_index] != 0 }
        excavator_half_use_qubo_binary_dict = {(excavator_index, truck_index): qubo.generate_qubo_binary(f'excavator_{excavator_index}_half_use_truck_{truck_index}') 
                                               for excavator_index in instance.excavator_list for truck_index in instance.truck_list 
                                               if et_match_dict[excavator_index][truck_index] != 0 }
        
        # Here we use other info to cal the truck number qubo dict
        truck_number_qubo_dict = { truck_index: self.qubo_util.kaiwu_sum_proxy(
                  excavator_truck_match_qubo_binary_dict[(excavator_index, truck_index)] * self.qubo_util.cal_ndarray_sum(excavator_number_qubo_dict[excavator_index])
                  * self.data.excavators_trucks_match_dict[excavator_index][truck_index] - excavator_half_use_qubo_binary_dict[(excavator_index, truck_index)] 
                  for excavator_index in self.instance.excavator_list if et_match_dict[excavator_index][truck_index] != 0 )
                                  for truck_index in instance.truck_list }
        return Variables(cost_constraint_num, 
                         excavator_number_qubo_dict, 
                         truck_number_qubo_dict, 
                         excavator_truck_match_qubo_binary_dict, 
                         excavator_half_use_qubo_binary_dict)
        
    def __excavator_purchase_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.excavator_precurement_cost[excavator_index] * qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) 
                for excavator_index in self.instance.excavator_list)
    
    def __excavator_oil_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.oil_price * data.excavator_oil_consumption[excavator_index] * qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index])
                for excavator_index in self.instance.excavator_list)
    
    def __truck_oil_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        
        return (data.oil_price * data.truck_oil_consumption[truck_index] * self.variables.truck_number_qubo_dict[truck_index]
                for truck_index in self.instance.truck_list)
    
    def __excavator_maintenance_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.excavator_maintenance_cost[excavator_index] * qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index])
                for excavator_index in self.instance.excavator_list)
    
    def __truck_maintenance_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.truck_maintenance_cost[truck_index] * self.variables.truck_number_qubo_dict[truck_index]
                for truck_index in self.instance.truck_list)
        
    def __produce_cost(self) -> Generator:
        qubo = self.qubo_util
        data  = self.data
        return (data.workdays_per_month * data.excavator_produce_efficiency[excavator_index] * 
                (qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) - 0.5 * 
                 self.variables.excavator_half_use_qubo_binary_dict[(excavator_index, truck_index)])
                for excavator_index in self.instance.excavator_list for truck_index in self.instance.truck_list
                    if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0 )
        
    def total_revenue(self, produce, oil_consumption_cost, maintenance_cost, precurement_cost):
        return 160 * 60 * produce - 160 * 60 * oil_consumption_cost - 60 * maintenance_cost - 10000 * precurement_cost
    
    def __budget_constraint(self):
        qubo = self.qubo_util
        data  = self.data
        precurement_cost = sum(qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) * data.excavator_precurement_cost[excavator_index] 
                for excavator_index in self.instance.excavator_list)
        return qubo.generate_qubo_constraint( 
            (data.total_budget - qubo.cal_ndarray_sum(self.variables.cost_constraint_num) - precurement_cost )
                                    , 'budget_constraint')
    
    def __excavator_match_constraint(self) -> dict:
        qubo = self.qubo_util
        excavator_match_constraint_dict = {}
        for excavator_index in self.instance.excavator_list:
            excavator_match_constraint_dict[excavator_index] = qubo.generate_qubo_constraint(qubo.kaiwu_sum_proxy(
                self.variables.excavator_truck_match_qubo_binary_dict[(excavator_index, truck_index)]
                for truck_index in self.instance.truck_list 
                if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0) - 1,
                f'excavator_{excavator_index}_match_constraint')
        return excavator_match_constraint_dict
    
    def __truck_match_constraint(self) -> dict:
        qubo = self.qubo_util
        truck_match_constraint_dict = {}
        for truck_index in self.instance.truck_list:
            truck_match_constraint_dict[truck_index] = qubo.generate_qubo_constraint(qubo.kaiwu_sum_proxy(
                self.variables.excavator_truck_match_qubo_binary_dict[(excavator_index, truck_index)]
                for excavator_index in self.instance.excavator_list 
                if self.data.excavators_trucks_match_dict[excavator_index][truck_index] != 0) - 1,
                f'truck_{truck_index}_match_constraint')
        return truck_match_constraint_dict
    
    def __half_use_constraint(self) -> dict:
        qubo = self.qubo_util
        et_match_dict = self.data.excavators_trucks_match_dict
        half_use_constraint_dict = {}
        for excavator_index in self.instance.excavator_list:
            for truck_index in self.instance.truck_list:
                if self.data.excavators_trucks_match_dict[excavator_index][truck_index] == 0:
                    continue
                half_use_constraint_dict[(excavator_index, truck_index)] = qubo.generate_qubo_constraint(
                    qubo.cal_ndarray_sum(self.variables.excavator_number_qubo_dict[excavator_index]) 
                    - et_match_dict[excavator_index][truck_index] * self.variables.excavator_truck_match_qubo_binary_dict[(excavator_index, truck_index)]
                    - self.variables.excavator_half_use_qubo_binary_dict[(excavator_index, truck_index)],
                    f'excavator_{excavator_index}_half_use_truck_{truck_index}_constraint')
        return half_use_constraint_dict
    
    def qubo_expr_object(self):
        qubo = self.qubo_util
        BUDGET_PARAM    = 30000000000
        EXCAVATOR_PARAM = 100000000000
        TRUCK_PARAM     = 100000000000
        
        produce = qubo.kaiwu_sum_proxy(self.__produce_cost())
        oil_consumption_cost = qubo.kaiwu_sum_proxy(self.__truck_oil_cost()) + qubo.kaiwu_sum_proxy(self.__excavator_oil_cost())
        maintenance_cost = qubo.kaiwu_sum_proxy(self.__excavator_maintenance_cost()) + qubo.kaiwu_sum_proxy(self.__truck_maintenance_cost())
        precurement_cost = qubo.kaiwu_sum_proxy(self.__excavator_purchase_cost())
        total_revenue = self.total_revenue(produce, oil_consumption_cost, maintenance_cost, precurement_cost)
        
        budget_constraint = self.__budget_constraint()
        excavator_match_constraint_dict = self.__excavator_match_constraint()
        truck_match_constraint_dict = self.__truck_match_constraint()
        half_use_constraint_dict = self.__half_use_constraint()
        
        qubo_solution = QuboSolution(self.variables, produce, oil_consumption_cost, maintenance_cost, precurement_cost, total_revenue, budget_constraint, excavator_match_constraint_dict, truck_match_constraint_dict, half_use_constraint_dict)
        
        object = - total_revenue + BUDGET_PARAM * budget_constraint + EXCAVATOR_PARAM * sum(excavator_match_constraint_dict.values()) \
         + TRUCK_PARAM * sum(truck_match_constraint_dict.values())
        return object, qubo_solution

    def solve_ising(self):
        qubo = self.qubo_util

        qubo_object, qubo_solution = self.qubo_expr_object()
        
        object = qubo.qubo_make_proxy(qubo_object)
        obj_ising = qubo.cim_ising_model_proxy(object)
        matrix = obj_ising.get_ising()["ising"]
        
        output = qubo.cim_simulator(matrix,
    	    pump=1.3,
            noise=0.3,
            laps=8000,
            dt=0.1,
            normalization=1.2,
            iterations=100
        )
        
        options = qubo.optimal_sampler(matrix, output)
        for index in range(20):
            qubo_dict = qubo.get_qubo_dict(options[0][index], obj_ising)

            solution_value = qubo_solution.get_value_from_qubo_dict(qubo_dict)
            solution_value.print_solution()
        return options