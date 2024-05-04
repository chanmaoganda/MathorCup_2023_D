from typing import Callable, Dict, Generator

from numpy import ndarray
import kaiwu
from utils import int2binary

class QuboUtil:
    def __init__(self):
        self.total_bits : int = 0
    
    def convert_qubo_ndarray_from_number(self, number : int, name : str) -> ndarray:
        current_bits = int2binary(number)
        self.total_bits += current_bits
        return kaiwu.qubo.ndarray(current_bits, name, kaiwu.qubo.binary)
    
    def convert_qubo_ndarray_from_bits(self, bits: int, name : str) -> ndarray:
        self.total_bits += bits
        return kaiwu.qubo.ndarray(bits, name, kaiwu.qubo.binary)
    
    def convert_qubo_binary(self, name : str):
        self.total_bits += 1
        return kaiwu.qubo.binary(name)
    
    def kaiwu_sum_proxy(self, generator: Generator):
        return kaiwu.qubo.sum(generator)
    
    def make_qubo_ndarray_condition_sum(self, qubo_array: ndarray, index_condition: Callable) :
        return kaiwu.qubo.sum(qubo_array[index] * ( 2 ** index ) for index in range(len(qubo_array)) if index_condition(index))
    
    def make_qubo_ndarray_sum(self, qubo_array: ndarray):
        return self.make_qubo_ndarray_condition_sum(qubo_array, lambda index: True)

    def convert_qubo_constraint(self, constraint, name : str):
        return kaiwu.qubo.constraint((constraint) ** 2, name)
    
    def show_detail(self, qubo_expr):
        kaiwu.qubo.details(qubo_expr)
        
    def show_dict_detail(self, qubo_dict: Dict):
        for key, value in qubo_dict.items():
            self.show_detail(value)
            
    def qubo_make_proxy(self, qubo_model):
        return kaiwu.qubo.make(qubo_model)
    
    def cim_ising_model_proxy(self, qubo_model):
        return kaiwu.qubo.cim_ising_model(qubo_model)
    
    def cim_simulator(self, matrix, pump = 1.3, noise = 0.3, laps = 5000, dt = 0.1, normalization = 1.3, iterations = 100):
        return kaiwu.cim.simulator(matrix, pump, noise, laps, dt, normalization, iterations)
    
    def optimal_sampler(self, matrix: ndarray, output: ndarray, bias = 0, negtail_ff = False):
        return kaiwu.sampler.optimal_sampler(matrix, output, bias, negtail_ff)
    
    def get_sol_dict(self, cim_best, vars):
        return kaiwu.qubo.get_sol_dict(cim_best, vars)
    
    def get_val(self, obj, sol_dict):
        return kaiwu.qubo.get_val(obj, sol_dict)
    
    def read_nums_from_dict(self, source_dict: Dict[str, ndarray], sol_dict) -> Dict[str, float]:
        return {name : sum(self.get_val(bit, sol_dict) * (2 ** bit_index) for bit_index, bit in enumerate(bits)) for name, bits in source_dict.items()}

    def read_constraint_from_dict(self, constraint_dict: dict, sol_dict):
        return {name : self.get_val(constraint, sol_dict) for name, constraint in constraint_dict.items()}
    
    def read_bits_from_dict(self, bits_dict: dict, sol_dict):
        return {name : self.get_val(bit_name, sol_dict) for name, bit_name in bits_dict.items()}
    
    def read_num_from_dict(self, source_array: ndarray, sol_dict):
        return sum(self.get_val(bit_name, sol_dict) * (2 ** bit_index) for bit_index, bit_name in enumerate(source_array))