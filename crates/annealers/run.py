#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python

import random
from JobShopWithArgs import JobShopWithArgs
import time

from InstanceMaker import InstanceMaker
from Instance import Instance

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
    