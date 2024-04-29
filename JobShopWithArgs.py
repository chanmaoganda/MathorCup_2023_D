import array
import kaiwu as kw
from math import ceil, log2
from utils import *

class JobShopWithArgs:
    def __init__(self, excavators: list, trucks: list):
        self.excavator_truck_dict: dict = { excavator: truck for excavator, truck in zip(excavators, trucks)}

    def solve(self):
        print(self.excavator_truck_dict)
        
    def print_solution(self):
        print("Solution:")
        
    def __int2binary(self, number: int):
        return ceil(log2(number + 1))

