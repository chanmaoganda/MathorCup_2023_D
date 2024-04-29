import array
from DataStorage import DataStorage
from QuboUtil import QuboUtil
import kaiwu as kw
from math import ceil, log2
from utils import *

class JobShopWithArgs:
    def __init__(self, excavators: list, trucks: list):
        self.excavator_truck_dict: dict = { excavator: truck for excavator, truck in zip(excavators, trucks)}
        self.data = DataStorage(total_budget = 2400, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                                excavator_oil_consumption = [28,30,34,38], truck_oil_cosumption = [18, 22, 27],
                                excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                                excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                                excavator_precurement_cost = [100, 140, 300, 320], 
                                excavator_truck_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]})
        self.qubo_util = QuboUtil()

    def solve(self):
        self.max_purchases = [self.data.total_budget // cost for cost in self.data.excavator_precurement_cost]
        self.bits_per_purcahse = list(get_mapped_generator(self.max_purchases, int2binary))
        machine_vars = dict()
        for index, bits in enumerate(self.bits_per_purcahse):
            if index not in self.excavator_truck_dict.keys():
                continue
            name = f'excavator{index}'
            machine_vars[name] = self.qubo_util.convert_qubo_ndarray(bits, name)
        print(machine_vars)
        print(self.bits_per_purcahse)
        
    def print_solution(self):
        print("Solution:")

