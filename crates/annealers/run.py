#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python
from typing import List
from JobShopWithArgs import JobShopWithArgs    
from multiprocessing import Pool
import time

def solve_one_instance(excavator_list: List[int]):
    
    pool = Pool(processes=16)
    pool.map(solve_one_instance, )

    jobshop = JobShopWithArgs(excavator_list, [0, 1, 2], iteration)
    # print(jobshop.make_all_instances())
    jobshop.solve()

def solve_all_instances(num_processes : int):
    start = time.time()
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    
# solve_all_instances(1000)
solve_one_instance(1)