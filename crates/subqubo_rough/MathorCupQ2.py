import kaiwu as kw
from math import log2, ceil
from subqubo_solver import SubQuboSolver, SubQuboVariable

def to_bin(num):
    """
    计算整数变量需要转化成多少位二进制数的函数
    :param num: 十进制数
    :return: 二进制数
    """
    bin = int(ceil(log2(num + 1)))
    return bin


# 成本数据
glb_costs = [100, 140, 200, 320]
glb_total_budget = 1760
glb_V = [0.9,1.2,0.8,2.1]  # Excavator bucket capacity
glb_R =[190,175,165,150]  # Excavator operational efficiency
glb_C_oil_i = [28,30,34,38] # Excavator oil consumption
glb_C_cai = [100,140,300,320]  # Excavator procurement cost
glb_C_ren_i = [7000,7500,8500,9000]  # Excavator labor cost
glb_C_wei_i =[1000,1500,2000,3000]  # Excavator maintenance cost

glb_C_oil_j = [18,22,27]  # Truck oil consumption
glb_C_ren_j = [6000,7000,8000]  # Truck labor cost
glb_C_wei_j =[2000,3000,4000]  # Truck maintenance cost

glb_n = [7,7,3] # Number of trucks of type j
glb_et = [[1, 0, 0], [2, 1, 0], [2, 2, 1], [0, 2, 1]]
glb_static_y = [0,1,3]

solver = SubQuboSolver(glb_et, glb_V, glb_R, glb_C_oil_i, glb_C_cai, glb_C_ren_i, glb_C_wei_i
                      , glb_C_oil_j, glb_C_ren_j, glb_C_wei_j, glb_total_budget, glb_costs)

variables = SubQuboVariable(glb_n, glb_static_y)
solver.solve(variables)