from JobShopWithArgs import JobShopWithArgs    
import sys

jobshop = JobShopWithArgs([0, 1, 3], [0, 1, 2], int(sys.argv[1]))

jobshop.solve()
