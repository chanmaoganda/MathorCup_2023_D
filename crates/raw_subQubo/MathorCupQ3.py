k_val = {'k_0_0': 0, 'k_0_1': 0, 'k_0_2': 5, 'k_1_0': 0, 'k_1_1': 0, 'k_1_2': 0, 'k_1_3': 4, 'k_2_0': 0, 'k_2_1': 0, 'k_2_2': 0, 'k_2_3': 0, 'k_2_4': 0, 'k_3_0': 5, 'k_3_1': 0, 'k_3_2': 0, 'k_3_3': 0, 'k_3_4': 0, 'k_3_5': 0, 'k_4_2': 0, 'k_4_3': 0, 'k_4_4': 0, 'k_4_5': 0, 'k_4_6': 0, 'k_4_7': 0, 'k_4_8': 0, 'k_5_2': 0, 'k_5_3': 0, 'k_5_4': 0, 'k_5_5': 0, 'k_5_6': 0, 'k_5_7': 2, 'k_5_8': 0, 'k_6_2': 0, 'k_6_3': 0, 'k_6_4': 0, 'k_6_5': 0, 'k_6_6': 0, 'k_6_7': 0, 'k_6_8': 0, 'k_6_9': 0, 'k_7_3': 0, 'k_7_4': 0, 'k_7_5': 0, 'k_7_6': 0, 'k_7_7': 0, 'k_7_8': 0, 'k_7_9': 0, 'k_8_4': 0, 'k_8_5': 0, 'k_8_6': 0, 'k_8_7': 0, 'k_8_8': 0, 'k_8_9': 0, 'k_9_5': 0, 'k_9_6': 0, 'k_9_7': 0, 'k_9_8': 3, 'k_9_9': 0}

import kaiwu as kw
from math import log2, ceil
from DataStorage import DataStorage
from utils import *

# Assume placeholder sets I for excavators and J for trucks, replace with actual sets.
I = 10  # Replace with actual excavator types
J = 10 # Replace with actual truck types
total_budget = 1760
# Placeholder parameters, replace with actual data
V = [0.9,1.2,0.8,2.1,2.6,3.5,5,6,8,10]  # Excavator bucket capacity
R =[190,175,165,150,140,130,120,110,105,100]  # Excavator operational efficiency
C_oil_i = [28,30,34,38,42,50,60,75,90,100] # Excavator oil consumption
# C_cai = [100,140,300,320,440,500,640,760,860,1000]  # Excavator procurement cost
C_ren_i = [7000,7500,8500,9000,10000,12000,13000,16000,18000,20000]  # Excavator labor cost
C_wei_i =[1000,1500,2000,3000,5000,8000,10000,13000,15000,18000]  # Excavator maintenance cost

C_oil_j = [15,18,22,27,33,40,50,55,64,70]  # Truck oil consumption
C_ren_j = [5000,6000,7000,8000,9000,10000,11000,12000,13000,15000]  # Truck labor cost
C_wei_j =[1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]  # Truck maintenance cost


n = [5,5,5,5,5,3,3,3,3,3] # Number of trucks of type j

m = [[3,3,2,0,0,0,0,0,0,0],
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

excavator_truck_dict = {index : m[index] for index in range(len(m))}
data = DataStorage(total_budget, V, R, C_oil_i, C_oil_j, C_ren_i, C_ren_j, C_wei_i, C_wei_j, costs, excavator_truck_dict, n)


# 定义记录变量数目的变量
cnt = 0

# 建立子问题1的挖掘机
sub1_eva = [0,1,2,3]
sub1_truck = [0,1,2,3,4,5]
# 为每种挖掘机计算最大购买数量
max_purchases = [total_budget // cost for cost in costs]
# 计算表示每个数量所需的二进制变量数 xi所对应的ti的数量
bits_per_purchase = [int2binary(purchase) for purchase in max_purchases]
# 计算需要添加的辅助变量的二进制位数
bits_purchase_s = [int(ceil(log2(bits + 1))) for bits in bits_per_purchase]



# 对于每个挖掘机，创建购买数量的二进制变量 ti
machine_vars = {}
for i, n_bits in enumerate(bits_per_purchase):
    if i in sub1_eva:
        # 创建每种挖掘机所需数量的二进制变量 ti
        machine_vars[f'machine{i}'] = kw.qubo.ndarray(n_bits, f"machine{i}", kw.qubo.binary)
        cnt += n_bits

# 创建k变量，表示i挖机分配的j矿车的数量
k = {}
zij = {}
for i in range(I):
    if i in sub1_eva:
        for j in range(J):
            if j in sub1_truck:
                if m[i][j]!=0:
                    if k_val[f'k_{i}_{j}'] !=0:
                        k[f'k_{i}_{j}'] = kw.qubo.ndarray(int2binary(n[j]),f'k_{i}_{j}',kw.qubo.binary)
                        zij[f'z_{i}_{j}'] = kw.qubo.binary(f'z{i}{j}')
                        cnt += (int2binary(n[j])+1)



cost_con_num = int(ceil(log2(1840 - 100 - 140 - 320)))
cost_con_s = kw.qubo.ndarray(cost_con_num,'cost_con_s',kw.qubo.binary)
cnt += cost_con_num

# 建立矿车数量的辅助变量
truck_s = {}
for j in range(J):
    if j in sub1_truck:
        truck_s[f'truck{j}'] = kw.qubo.ndarray(int2binary(n[j]),f'truck{j}_s',kw.qubo.binary)
        cnt += int2binary(n[j])
print('建立的变量总数为：',cnt)
# 计算总成本表达式
total_cost_expression = kw.qubo.sum(
    kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) * costs[i]
    for i in range(len(costs)) if i in sub1_eva)

cost_s_expression = kw.qubo.sum(cost_con_s[i] * (2**i) for i in range(cost_con_num))
# 构建成本约束
budget_constraint = kw.qubo.constraint((total_budget - total_cost_expression - cost_s_expression)**2, name="budget")


# 分配的矿车数量小于矿车总数的约束
truck_constraints = {}
for j in range(J):
    if j in sub1_truck:
        truck_constraints[f'tru_con{j}'] = kw.qubo.constraint((n[j] - kw.qubo.sum(kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if f'k_{i}_{j}' in k) - kw.qubo.sum(truck_s[f'truck{j}'][m] * (2**m) for m in range(len(truck_s[f'truck{j}']))))**2,name =f'tru_con{j}' )

# 计算zij的约束
zij_cons = {}
for i in range(I):
    if i in sub1_eva:
        for j in range(J):
            if j in sub1_truck:
                if m[i][j]!=0:
                    if k_val[f'k_{i}_{j}']!=0:
                        zij_cons[f'z{i}{j}'] = kw.qubo.constraint((kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}'])))+(zij[f'z_{i}_{j}'])-m[i][j]* kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**m) for m in range(len(machine_vars[f'machine{i}']))))**2,name=f'zcons{i}{j}')

total_revenue = 160 * kw.qubo.sum(
    V[i] * R[i] * 20 * (kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) - 0.5 * kw.qubo.sum(zij[f'z_{i}_{j}'] for j in range(J) if f'z_{i}_{j}' in zij and j in sub1_truck))
    for i in range(I) if i in sub1_eva
)*60 - 160*kw.qubo.sum(
    C_oil_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub1_eva
)*60 - 160*kw.qubo.sum(
    C_oil_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) for j in range(J) if f'k_{i}_{j}' in k and j in sub1_truck
)*60 - kw.qubo.sum(
    C_ren_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub1_eva
)*60 - kw.qubo.sum(
    C_wei_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub1_eva
)*60 - kw.qubo.sum(
    C_ren_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if i in sub1_eva for j in range(J)if f'k_{i}_{j}' in k and j in sub1_truck
) * 60 - kw.qubo.sum(
    C_wei_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if i in sub1_eva for j in range(J)if f'k_{i}_{j}' in k and j in sub1_truck
) * 60 - kw.qubo.sum(
    costs[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) * 10000 for i in range(I) if i in sub1_eva
)


obj = (-total_revenue + 30000000*budget_constraint
    + kw.qubo.sum(30000000*truck_constraints[f'tru_con{j}'] for j in range(J) if j in sub1_truck)
       + kw.qubo.sum(30000000*zij_cons[f'z{i}{j}'] for i in range(I) if i in sub1_eva for j in range(J) if f'k_{i}_{j}' in k and j in sub1_truck)
       )

obj = kw.qubo.make(obj)

obj_ising = kw.qubo.cim_ising_model(obj)

matrix = obj_ising.get_ising()["ising"]

# 使用 CIM 模拟器执行计算
output = kw.cim.simulator(
    matrix,
    pump=1.3,
    noise=0.2,
    laps=5000,
    dt=0.1,
    normalization=1.3,
    iterations=100)
# 对结果进行排序并选择最佳解
opt = kw.sampler.optimal_sampler(matrix, output, bias=0, negtail_ff=False)
best = opt[0][0]
# If the linear term variable is -1, perform a flip
cim_best = best * best[-1]
# Get the list of variable names
vars = obj_ising.get_variables()
# Substitute the spin vector and obtain the result dictionary
sol_dict = kw.qubo.get_sol_dict(cim_best, vars)

obj_val = kw.qubo.get_val(obj, sol_dict)
objective_function_val = kw.qubo.get_val(total_revenue, sol_dict)
budget_constraint_val = kw.qubo.get_val(budget_constraint, sol_dict)

truck_constraints_val = {}
for j in range(3):
    truck_constraints_val[f'val{j}'] = kw.qubo.get_val(truck_constraints[f'tru_con{j}'], sol_dict)

zij_cons_val = {}
for i in range(4):
    if i in sub1_eva:
        for j in range(3):
            if f'k_{i}_{j}' in k:
              zij_cons_val[f'z{i}{j}'] = kw.qubo.get_val(zij_cons[f'z{i}{j}'], sol_dict)

# 从QUBO解中获取每种挖掘机的数量
machine_values = {}
for machine, bits in machine_vars.items():
    # 计算从二进制到整数的转换
    value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
    machine_values[machine] = value
k_values = {}
for k, bits in k.items():
    # 计算从二进制到整数的转换
    value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
    k_values[k] = value


# 输出结果
print('-------------------------子问题1的结果-------------------')
print('矿车的分配数量：')
for k, v in k_values.items():
    print(f"{k}: {v}")

# 初始化总成本和总利润变量
total_cost = 0
total_profit = 0

# 遍历每种挖掘机
for i, (machine, quantity) in enumerate(machine_values.items()):
    if i in sub1_eva:
        # 计算总成本
        total_cost += quantity * costs[i]

# 输出结果
print(f"总成本: {total_cost}")


print("每种挖掘机的购买数量:")
for k, v in machine_values.items():
    print(f"{k}: {v}")










# 定义记录变量数目的变量
cnt = 0

# 建立子问题1的挖掘机
sub2_eva = [5,6,8,9]
sub2_truck = [6,7,8,9]
# 为每种挖掘机计算最大购买数量
max_purchases = [total_budget // cost for cost in costs]
# 计算表示每个数量所需的二进制变量数 xi所对应的ti的数量
bits_per_purchase = [int2binary(purchase) for purchase in max_purchases]
# 计算需要添加的辅助变量的二进制位数
bits_purchase_s = [int(ceil(log2(bits + 1))) for bits in bits_per_purchase]



# 对于每个挖掘机，创建购买数量的二进制变量 ti
machine_vars = {}
for i, n_bits in enumerate(bits_per_purchase):
    if i in sub2_eva:
        # 创建每种挖掘机所需数量的二进制变量 ti
        machine_vars[f'machine{i}'] = kw.qubo.ndarray(n_bits, f"machine{i}", kw.qubo.binary)
        cnt += n_bits

# 创建k变量，表示i挖机分配的j矿车的数量
k = {}
zij = {}
for i in range(I):
    if i in sub2_eva:
        for j in range(J):
            if j in sub2_truck:
                if m[i][j]!=0:
                    if k_val[f'k_{i}_{j}'] !=0:
                        k[f'k_{i}_{j}'] = kw.qubo.ndarray(int2binary(n[j]),f'k_{i}_{j}',kw.qubo.binary)
                        zij[f'z_{i}_{j}'] = kw.qubo.binary(f'z{i}{j}')
                        cnt += (int2binary(n[j])+1)



cost_con_num = int(ceil(log2(1840-100-140- 320)))
cost_con_s = kw.qubo.ndarray(cost_con_num,'cost_con_s',kw.qubo.binary)
cnt += cost_con_num

# 建立矿车数量的辅助变量
truck_s = {}
for j in range(J):
    if j in sub2_truck:
        truck_s[f'truck{j}'] = kw.qubo.ndarray(int2binary(n[j]),f'truck{j}_s',kw.qubo.binary)
        cnt += int2binary(n[j])
print('建立的变量总数为：',cnt)
# 计算总成本表达式
total_cost_expression = kw.qubo.sum(
    kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) * costs[i]
    for i in range(len(costs)) if i in sub2_eva)

cost_s_expression = kw.qubo.sum(cost_con_s[i] * (2**i) for i in range(cost_con_num))
# 构建成本约束
budget_constraint = kw.qubo.constraint((total_budget - total_cost_expression - cost_s_expression)**2, name="budget")


# 分配的矿车数量小于矿车总数的约束
truck_constraints = {}
for j in range(J):
    if j in sub2_truck:
        truck_constraints[f'tru_con{j}'] = kw.qubo.constraint((n[j] - kw.qubo.sum(kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if f'k_{i}_{j}' in k) - kw.qubo.sum(truck_s[f'truck{j}'][m] * (2**m) for m in range(len(truck_s[f'truck{j}']))))**2,name =f'tru_con{j}' )

# 计算zij的约束
zij_cons = {}
for i in range(I):
    if i in sub2_eva:
        for j in range(J):
            if j in sub2_truck:
                if m[i][j]!=0:
                    if k_val[f'k_{i}_{j}']!=0:
                        if len(k[f'k_{i}_{j}']) > 0 and len(machine_vars[f'machine{i}']) > j:
                            zij_cons[f'z{i}{j}'] = kw.qubo.constraint((kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}'])))+(zij[f'z_{i}_{j}'])-m[i][j]* kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**m) for m in range(len(machine_vars[f'machine{i}']))))**2,name=f'zcons{i}{j}')

total_revenue = 160 * kw.qubo.sum(
    V[i] * R[i] * 20 * (kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) - 0.5 * kw.qubo.sum(zij[f'z_{i}_{j}'] for j in range(J) if f'z_{i}_{j}' in zij and j in sub2_truck))
    for i in range(I) if i in sub2_eva
)*60 - 160*kw.qubo.sum(
    C_oil_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub2_eva
)*60 - 160*kw.qubo.sum(
    C_oil_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) for j in range(J) if f'k_{i}_{j}' in k and j in sub2_truck
)*60 - kw.qubo.sum(
    C_ren_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub2_eva
)*60 - kw.qubo.sum(
    C_wei_i[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) for i in range(I) if i in sub2_eva
)*60 - kw.qubo.sum(
    C_ren_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if i in sub2_eva for j in range(J)if f'k_{i}_{j}' in k and j in sub2_truck
) * 60 - kw.qubo.sum(
    C_wei_j[j] * kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if i in sub2_eva for j in range(J)if f'k_{i}_{j}' in k and j in sub2_truck
) * 60 - kw.qubo.sum(
    costs[i] * kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) * 10000 for i in range(I) if i in sub2_eva
)


obj = (-total_revenue + 30000000*budget_constraint
    + kw.qubo.sum(30000000*truck_constraints[f'tru_con{j}'] for j in range(J) if j in sub2_truck)
       + kw.qubo.sum(30000000*zij_cons[f'z{i}{j}'] for i in range(I) if i in sub2_eva for j in range(J) if f'k_{i}_{j}' in k and j in sub2_truck and f'z{i}{j}' in zij_cons)
       )

obj = kw.qubo.make(obj)

obj_ising = kw.qubo.cim_ising_model(obj)

matrix = obj_ising.get_ising()["ising"]

# 使用 CIM 模拟器执行计算
output = kw.cim.simulator(
    matrix,
    pump=1.3,
    noise=0.2,
    laps=5000,
    dt=0.1,
    normalization=1.3,
    iterations=100)
# 对结果进行排序并选择最佳解
opt = kw.sampler.optimal_sampler(matrix, output, bias=0, negtail_ff=False)
best = opt[0][0]
# If the linear term variable is -1, perform a flip
cim_best = best * best[-1]
# Get the list of variable names
vars = obj_ising.get_variables()
# Substitute the spin vector and obtain the result dictionary
sol_dict = kw.qubo.get_sol_dict(cim_best, vars)

obj_val = kw.qubo.get_val(obj, sol_dict)
objective_function_val = kw.qubo.get_val(total_revenue, sol_dict)
budget_constraint_val = kw.qubo.get_val(budget_constraint, sol_dict)

truck_constraints_val = {}
for j in range(J):
    if f'truck_con{j}' in truck_constraints:
        truck_constraints_val[f'val{j}'] = kw.qubo.get_val(truck_constraints[f'truck_con{j}'], sol_dict)

zij_cons_val = {}
for i in range(I):
    if i in sub2_eva:
        for j in range(3):
            if f'k_{i}_{j}' in k:
              zij_cons_val[f'z{i}{j}'] = kw.qubo.get_val(zij_cons[f'z{i}{j}'], sol_dict)

# 从QUBO解中获取每种挖掘机的数量
machine_values = {}
for machine, bits in machine_vars.items():
    # 计算从二进制到整数的转换
    value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
    machine_values[machine] = value
k_values = {}
for k, bits in k.items():
    # 计算从二进制到整数的转换
    value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
    k_values[k] = value


# 输出结果
print('-------------------------子问题2的结果-------------------')
print('矿车的分配数量：')
for k, v in k_values.items():
    print(f"{k}: {v}")

# 初始化总成本和总利润变量
total_cost = 0
total_profit = 0

# 遍历每种挖掘机
for i, (machine, quantity) in enumerate(machine_values.items()):
        # 计算总成本
        total_cost += quantity * costs[i]

# 输出结果
print(f"总成本: {total_cost}")


print("每种挖掘机的购买数量:")
for k, v in machine_values.items():
    print(f"{k}: {v}")
