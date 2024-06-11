from QuboUtil import QuboUtil
from UtilClasses import *

class QuboExprGenerator:
    def __init__(self, qubo_util: QuboUtil, variables: Variables):
        self.qubo_util = qubo_util
        self.variables = variables