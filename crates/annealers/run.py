#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python

import random
from JobShopWithArgs import JobShopWithArgs
import time

from InstanceMaker import InstanceMaker
from Instance import Instance
from DataStorage import DataStorage

def solve_one_instance_one_iteration():
    instance_maker : InstanceMaker = InstanceMaker()
    instances = instance_maker.make_combinations()
    # TODO: I need to randomly select an instance from the list of instances 
    # TODO: and then select part of them to run and compare the results.
    # TODO: Also, the truck list is intended to be generated randomly, so I need to fix that.
    random_index = random.randint(0, len(instances) - 1)
    random_instance = instances[random_index]
    
    instance_solver : Instance = Instance(random_instance, [], instance_maker.data)
    MAX_ITERATION_NUMBER = 1000
    
    for i in range(MAX_ITERATION_NUMBER):
        # TODO: Select a random part of the instance to run and compare the results.
        sub_instance = instance_solver
        sub_job_shop = JobShopWithArgs(sub_instance)
        
        
    jobshop = JobShopWithArgs(instance_solver)
    jobshop.solve()

data = DataStorage(total_budget = 2400, excavator_bucket = [0.9, 1.2, 0.8, 2.1], excavator_efficiency = [190, 175, 165, 150], 
                    excavator_oil_consumption = [28,30,34,38], truck_oil_consumption = [18, 22, 27],
                    excavator_labor_cost = [7000, 7500, 8500, 9000], truck_labor_cost = [6000, 7000, 8000],
                    excavator_maintenance_cost = [1000, 1500, 2000, 3000], truck_maintenance_cost = [2000, 3000, 4000],
                    excavator_precurement_cost = [100, 140, 300, 320], 
                    excavators_trucks_match_dict = { 0 : [1, 0, 0], 1 : [2, 1, 0], 2: [2, 2, 1], 3: [0, 2, 1]},
                    total_truck_numbers = [7, 7, 3])

instance = Instance([0, 1, 3], [0, 1, 2], data)
job_shop = JobShopWithArgs(instance)
job_shop.solve()