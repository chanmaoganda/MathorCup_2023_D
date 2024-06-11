from numpy import ndarray

from utils import *
from typing import Dict
from Instance import Instance
from UtilClasses import *
from QuboUtil import QuboUtil
from UtilClasses import Variables
from QuboExprGenerator import QuboExprGenerator

class SubQuboSolver:
    data: DataStorage
    
    def __init__(self, instance: Instance):
        self.data = instance.data
        self.sequence_number = instance.iteration

        self.qubo_util = QuboUtil()
        self.qubo_expr_generator = QuboExprGenerator(self.qubo_util, instance)
        

    def generate_qubo_constraints(self, variables: Variables):
        qubo = self.qubo_util
        data = self.data
        
        