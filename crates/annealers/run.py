#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python
import random
from typing import List
from JobShopWithArgs import JobShopWithArgs    
from multiprocessing import Pool
import time

from InstanceMaker import InstanceMaker
from Instance import Instance

def solve_one_instance_one_iteration():
    instance_maker : InstanceMaker = InstanceMaker()
    instances = instance_maker.make_combinations()
    # TODO: I need to randomly select an instance from the list of instances 
    # TODO: and then select part of them to run and compare the results.
    # TODO: Also, the truck list is intended to be generated randomly, so I need to fix that.
    random_index = random.randint(0, len(instances)-1)
    random_instance = instances[random_index]
    
    instance_solver : Instance = Instance(random_instance, [], instance_maker.data)
    
    jobshop = JobShopWithArgs(instance_solver)
    jobshop.solve()
    