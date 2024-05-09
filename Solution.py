from typing import Dict

from numpy import ndarray


class Solution:
    def __init__(self, obj, total_revenue, excavator_numbers: Dict, truck_numbers: Dict, half_used_excavator_bits: dict, cost_con_s, 
                budget_constraint, truck_num_constraint, produce, oil_consume, maintenance, precurement):
        self.obj = obj
        self.total_revenue = total_revenue
        self.excavator_numbers = excavator_numbers
        self.truck_numbers = truck_numbers
        self.half_used_excavator_bits = half_used_excavator_bits
        self.cost_con_s = cost_con_s
        self.budget_constraint = budget_constraint
        self.truck_num_constraint = truck_num_constraint
        self.produce = produce
        self.oil_consume = oil_consume
        self.maintenance = maintenance
        self.precurement = precurement