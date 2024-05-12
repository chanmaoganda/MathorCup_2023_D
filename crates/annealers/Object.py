class Object:
    def __init__(self, total_cost, 
                 cost_con_value, 
                 budget_constraint_val, 
                 truck_num_constraint_val, 
                 excavator_values, truck_values, 
                 half_used_values, 
                 total_revenue_val, 
                 obj_val, 
                 produce_cost, 
                 oil_consume_cost, 
                 maintenance_cost, 
                 precurement_cost, 
                 excavator_produce_dict): 
        self.total_cost = total_cost
        self.cost_con_value = cost_con_value
        self.budget_constraint_val = budget_constraint_val
        self.truck_num_constraint_val = truck_num_constraint_val
        self.excavator_values = excavator_values
        self.truck_values = truck_values
        self.half_used_values = half_used_values
        self.total_revenue_val = total_revenue_val
        self.obj_val = obj_val
        self.produce_cost = produce_cost
        self.oil_consume_cost = oil_consume_cost
        self.maintenance_cost = maintenance_cost
        self.precurement_cost = precurement_cost
        self.excavator_produce_dict = excavator_produce_dict
            