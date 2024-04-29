import kaiwu
from utils import int2binary


class QuboUtil:
    def __init__(self):
        self.total_bits : int = 0
    
    def convert_qubo_ndarray(self, number : int, name : str):
        current_bits = int2binary(number)
        self.total_bits += current_bits
        return kaiwu.qubo.ndarray(current_bits, name, kaiwu.qubo.binary)
    
    def convert_qubo_binary(self, name : str):
        self.total_bits += 1
        return kaiwu.qubo.binary(name)
    
    