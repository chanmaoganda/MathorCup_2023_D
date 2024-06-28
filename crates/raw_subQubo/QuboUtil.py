from typing import Callable, Dict, Generator

from numpy import ndarray
import kaiwu
from utils import int2binary

class QuboUtil:
    def __init__(self):
        self.total_bits : int = 0
    
    def ndarray_from_number(self, number : int, name : str) -> ndarray:
        """
        this function generates a qubo ndarray from a number.
        it will auto convert number to suitable bits and convert it to a qubo ndarray.
        
        Parameters
        ----------
        param number: the number to be converted to qubo ndarray
        param name: the name of the qubo ndarray
        """
        current_bits = int2binary(number)
        self.total_bits += current_bits
        return kaiwu.qubo.ndarray(current_bits, name, kaiwu.qubo.binary)
    
    def ndarray_from_bits(self, bits: int, name : str) -> ndarray:
        """
        this function generates a qubo ndarray from the number of bits.
        
        Parameters
        ----------
        param bits: the number of bits to be converted to qubo ndarray
        param name: the name of the qubo ndarray
        """
        self.total_bits += bits
        return kaiwu.qubo.ndarray(bits, name, kaiwu.qubo.binary)
    
    def generate_qubo_binary(self, name : str):
        """
        this function generates a qubo binary variable.
        
        Parameters
        ----------
        param name: the name of the qubo binary variable
        """
        self.total_bits += 1
        return kaiwu.qubo.binary(name)
    
    def kaiwu_sum_proxy(self, generator: Generator):
        """
        calculates the sum of a generator of qubo expressions.
        
        Parameters
        ----------
        param generator: the generator of `qubo expressions`.
        """
        return kaiwu.qubo.sum(generator)
    
    def __make_qubo_ndarray_condition_sum(self, qubo_array: ndarray, index_condition: Callable) :
        return kaiwu.qubo.sum(qubo_array[index] * ( 2 ** index ) for index in range(len(qubo_array)) if index_condition(index))
    
    def cal_ndarray_sum(self, qubo_array: ndarray):
        """
        calculates the sum of a qubo ndarray
        In most cases, calculate the `real value` from the bits stored in qubo_ndarray.
        
        Parameters
        ----------
        param qubo_array: the qubo ndarray to be calculated.
        
        Examples
        --------
        >>> qubo_number = self.ndarray_from_number(10, "qubo_array")
        >>> qubo_expr = self.cal_ndarray_sum(qubo_array)
        
        """
        return self.__make_qubo_ndarray_condition_sum(qubo_array, lambda index: True)

    def generate_qubo_constraint(self, constraint, name : str):
        """
        calculate the qubo constraint and make constraint from (@param constraint) ** 2
        
        Parameters
        ----------
        constraint: the constraint to be calculated.
        
        Examples
        --------
        >>> constraint: (qubo_number = 10)
        >>> qubo_number = self.ndarray_from_number(10, "qubo_array")
        >>> qubo_constraint = self.generate_qubo_constraint(qubo_number - 10, "qubo_constraint")
        
        """
        return kaiwu.qubo.constraint( (constraint) ** 2, name)
    
    
    
    
    def show_detail(self, qubo_expr):
        kaiwu.qubo.details(qubo_expr)
        
    def show_dict_detail(self, qubo_dict: Dict):
        for key, value in qubo_dict.items():
            self.show_detail(value)
            
    def qubo_make_proxy(self, qubo_model):
        return kaiwu.qubo.make(qubo_model)
    
    def cim_ising_model_proxy(self, qubo_model):
        return kaiwu.qubo.cim_ising_model(qubo_model)
    
    def cim_simulator(self, matrix, pump = 1.3, noise = 0.3, laps = 8000, dt = 0.1, normalization = 1.3, iterations = 100):
        return kaiwu.cim.simulator(matrix, pump, noise, laps, dt, normalization, iterations)
    
    def optimal_sampler(self, matrix: ndarray, output: ndarray, bias = 0, negtail_ff = False):
        return kaiwu.sampler.optimal_sampler(matrix, output, bias, negtail_ff)
    
    def get_sol_dict(self, cim_best, vars):
        return kaiwu.qubo.get_sol_dict(cim_best, vars)
    
    def read_value_from_solution(self, expression, sol_dict):
        """
        reads the actual value from the solution dictionary.
        
        Parameters
        ----------
        expression: it can be `qubo_binary`, `qubo_ndarray`, `qubo_constraint`
        sol_dict: the solution dictionary.
        
        Examples
        --------
        >>> qubo_number = self.ndarray_from_number(10, "qubo_array")
        >>> qubo_binary = self.generate_qubo_binary("qubo_binary")
        >>> qubo_constraint = self.generate_qubo_constraint(qubo_number - 10, "qubo_constraint")
        >>> ......
        >>> sol_dict = self.get_sol_dict(cim_best, vars)
        >>> qubo_binary_value = self.read_value_from_dict(qubo_binary, sol_dict)
        >>> qubo_number_value = self.read_value_from_dict(qubo_number, sol_dict)
        >>> qubo_constraint_value = self.read_value_from_dict(qubo_constraint, sol_dict)
        
        """
        if isinstance(expression, ndarray):
            return sum(kaiwu.qubo.get_val(bit, sol_dict) * (2 ** bit_index) for bit_index, bit in enumerate(expression))
        return kaiwu.qubo.get_val(expression, sol_dict)
    
    
    
    
    def read_dict_from_solution(self, source_dict: Dict, sol_dict) -> Dict:
        """
        read the actual values from the solution dictionary.
        
        Parameters
        ----------
        source_dict: the source dictionary.      the value type can be `qubo_binary`, `qubo_ndarray`, `qubo_constraint`.
        sol_dict: the solution dictionary.
        """
        return {name : self.read_value_from_solution(bits, sol_dict) for name, bits in source_dict.items()}

    def get_qubo_dict(self, option_result, obj_ising_model):
        cim_best = option_result * option_result[-1]
        vars = obj_ising_model.get_variables()
        return self.get_sol_dict(cim_best, vars)
        