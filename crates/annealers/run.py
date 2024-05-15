#!/home/avania/projects/python/MathorCupD-2023/.venv/bin/python
from JobShopWithArgs import JobShopWithArgs    
from multiprocessing import Pool
import time

def solve_one_instance(iteration : int):
    jobshop = JobShopWithArgs([0, 1, 3], [0, 1, 2], iteration)
    jobshop.solve()

def solve_all_instances(num_processes : int):
    start = time.time()
    pool = Pool(processes=16)
    pool.map(solve_one_instance, [index for index in range(1, num_processes)])
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    
solve_all_instances(1000)