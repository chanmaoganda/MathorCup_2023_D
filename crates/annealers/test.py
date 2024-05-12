from JobShopWithArgs import JobShopWithArgs    
import sys
from multiprocessing import Pool

pool = Pool(processes=8)

def solve_one_instance(iteration : int):
    jobshop = JobShopWithArgs([0, 1, 3], [0, 1, 2], iteration)
    jobshop.solve()

solve_one_instance(1)
# pool.map(solve_one_instance, range(10))
pool.close()
pool.join()