#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python
from typing import List
from JobShopWithArgs import JobShopWithArgs    
from multiprocessing import Pool
import time

from InstanceMaker import InstanceMaker
from InstanceSolver import InstanceSolver

def solve_one_instance_one_iteration(instance_solver : InstanceSolver):
    jobshop = JobShopWithArgs(instance_solver)
    jobshop.solve()

def solve_one_instance(instance_solvers: List[InstanceSolver]):
    pool = Pool(processes=16)
    pool.map(solve_one_instance_one_iteration, instance_solvers)

def solve_all_instances(num_processes : int):
    start = time.time()
    instance_maker = InstanceMaker()
    instances = instance_maker.make_all_instances()
    for instance in instances:
        instance_list: List[InstanceSolver] = [InstanceSolver(instance, instance_maker.data).assign_iteration(iteration) 
                        for iteration in range(num_processes)]
        solve_one_instance(instance_list)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    
solve_all_instances(10)