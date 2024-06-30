k_val = {'k_0_0': 0, 'k_0_1': 0, 'k_0_2': 5, 'k_1_0': 0, 'k_1_1': 0, 'k_1_2': 0, 'k_1_3': 4, 'k_2_0': 0, 'k_2_1': 0, 'k_2_2': 0, 'k_2_3': 0, 'k_2_4': 0, 'k_3_0': 5, 'k_3_1': 0, 'k_3_2': 0, 'k_3_3': 0, 'k_3_4': 0, 'k_3_5': 0, 'k_4_2': 0, 'k_4_3': 0, 'k_4_4': 0, 'k_4_5': 0, 'k_4_6': 0, 'k_4_7': 0, 'k_4_8': 0, 'k_5_2': 0, 'k_5_3': 0, 'k_5_4': 0, 'k_5_5': 0, 'k_5_6': 0, 'k_5_7': 2, 'k_5_8': 0, 'k_6_2': 0, 'k_6_3': 0, 'k_6_4': 0, 'k_6_5': 0, 'k_6_6': 0, 'k_6_7': 0, 'k_6_8': 0, 'k_6_9': 0, 'k_7_3': 0, 'k_7_4': 0, 'k_7_5': 0, 'k_7_6': 0, 'k_7_7': 0, 'k_7_8': 0, 'k_7_9': 0, 'k_8_4': 0, 'k_8_5': 0, 'k_8_6': 0, 'k_8_7': 0, 'k_8_8': 0, 'k_8_9': 0, 'k_9_5': 0, 'k_9_6': 0, 'k_9_7': 0, 'k_9_8': 3, 'k_9_9': 0}

import kaiwu as kw
from utils import *
from subqubo_solver import *

# Assume placeholder sets I for excavators and J for trucks, replace with actual sets.
I = 10  # Replace with actual excavator types
J = 10 # Replace with actual truck types
total_budget = 2400
# Placeholder parameters, replace with actual data
V = [0.9,1.2,0.8,2.1,2.6,3.5,5,6,8,10]  # Excavator bucket capacity
R =[190,175,165,150,140,130,120,110,105,100]  # Excavator operational efficiency
C_oil_i = [28,30,34,38,42,50,60,75,90,100] # Excavator oil consumption
C_cai = [100,140,300,320,440,500,640,760,860,1000]  # Excavator procurement cost
C_ren_i = [7000,7500,8500,9000,10000,12000,13000,16000,18000,20000]  # Excavator labor cost
C_wei_i =[1000,1500,2000,3000,5000,8000,10000,13000,15000,18000]  # Excavator maintenance cost

C_oil_j = [15,18,22,27,33,40,50,55,64,70]  # Truck oil consumption
C_ren_j = [5000,6000,7000,8000,9000,10000,11000,12000,13000,15000]  # Truck labor cost
C_wei_j =[1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]  # Truck maintenance cost

n = [5,5,5,5,5,3,3,3,3,3] # Number of trucks of type j

et =[
     [3,3,2,0,0,0,0,0,0,0],
     [3,3,3,2,0,0,0,0,0,0],
     [4,3,3,3,2,0,0,0,0,0],
     [5,4,3,3,3,2,0,0,0,0],
     [0,0,5,4,3,3,3,2,2,0],
     [0,0,5,4,3,3,3,2,2,0],
     [0,0,5,5,4,3,3,3,2,2],
     [0,0,0,5,5,4,3,3,3,3],
     [0,0,0,0,5,5,4,3,3,3],
     [0,0,0,0,0,5,5,4,3,3]]  # Excavator-truck requirements
costs =[100,140,300,320,440,500,640,760,860,1000]

subqubo_solver = SubQuboSolver(et, V, R, C_oil_i, C_cai, C_ren_i, C_wei_i, C_oil_j, C_ren_j, C_wei_j, total_budget, costs)

variables = SubQuboVariable([0, 1, 2], [0, 1, 2], 2400)
solution: SubQuboSolution = subqubo_solver.sub_qubo_best_solve(variables)

def gen_combinations():
    pass

