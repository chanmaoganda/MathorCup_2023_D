#!/home/avania/projects/python/qboson/codes/.venv/bin/python3
# -*- coding: utf-8 -*-
from typing import Callable, Generator
import pandas as pd
from QuboUtil import QuboUtil
import kaiwu as kw
from math import log2, ceil
from typing import List, Dict

def to_binary(num: int):
    """
    计算整数变量需要转化成多少位二进制数的函数
    :param num: 十进制数
    :return: 二进制数
    """
    bits = int(ceil(log2(num + 1)))
    return bits
def get_generator(source_array: List) -> Generator:
    return (source_array[j] * ( 2 ** j ) for j in range(len(source_array)))

def get_generator_conditionally(source_array: List, function: Callable[[int], bool]):
    return (source_array[j] * ( 2 ** j ) for j in range(len(source_array)) if function(source_array[j]))

# 成本数据
costs = [100, 140, 200, 320]
total_budget = 1760 # i was told to buy excavators 0, 1, 3
I = 4
# 矿车数量
J = 3
K = 3
# Placeholder parameters, replace with actual data
V = [0.9,1.2,0.8,2.1]  # Excavator bucket capacity
R =[190,175,165,150]  # Excavator operational efficiency
C_oil_i = [28,30,34,38] # Excavator oil consumption
C_oil_j = [18,22,27]  # Truck oil consumption
C_ren_i = [7000,7500,8500,9000]  # Excavator labor cost
C_ren_j = [6000,7000,8000]  # Truck labor cost
C_wei_i =[1000,1500,2000,3000]  # Excavator maintenance cost
C_wei_j =[2000,3000,4000]  # Truck maintenance cost
C_cai = [100,140,300,320]  # Excavator procurement cost
n = [6,6,2] # Number of trucks of type j
m = [[1,0,0], # 0
     [2,1,0], # 1
     [2,2,1], # 2
     [0,2,1]] # 3
# Excavator-truck requirements

# 定义记录变量数目的变量
total_used_bits = 0

# 建立变量的挖掘机
static_y = [0,1,3]
k_val ={'k_0_0': 7, 'k_1_0': 0, 'k_1_1': 7, 'k_2_0': 0, 'k_2_1': 0, 'k_2_2': 0, 'k_3_1': 0, 'k_3_2': 2}
# 为每种挖掘机计算最大购买数量
max_purchases = [total_budget // cost for cost in costs]
# 计算表示每个数量所需的二进制变量数 xi所对应的ti的数量
bits_per_purchase = [to_binary(purchase) for purchase in max_purchases]
# 计算需要添加的辅助变量的二进制位数
bits_purchase_s = [int(ceil(log2(bits + 1))) for bits in bits_per_purchase]

# 对于每个挖掘机，创建购买数量的二进制变量 ti
machine_vars = dict()
for i, n_bits in enumerate(bits_per_purchase):
    if i in static_y:
        # 创建每种挖掘机所需数量的二进制变量 ti
        machine_vars[f'machine{i}'] = kw.qubo.ndarray(n_bits, f"machine{i}", kw.qubo.binary)
        total_used_bits += n_bits

# 创建k变量，表示i挖机分配的j矿车的数量
k = {}
zij = {}
for i in range(I):
    if i not in static_y:
        continue
    for j in range(J):
        if m[i][j] == 0 or k_val[f'k_{i}_{j}'] == 0: # make sure machine i matches truck and ? TODO
            continue
        k[f'k_{i}_{j}'] = kw.qubo.ndarray(to_binary(n[j]), f'k_{i}_{j}', kw.qubo.binary)
        zij[f'z_{i}_{j}'] = kw.qubo.binary(f'z{i}{j}')
        total_used_bits += (to_binary(n[j]) + 1)

cost_con_num = int(ceil(log2(1840-100-140- 320)))
cost_con_s = kw.qubo.ndarray(cost_con_num,'cost_con_s',kw.qubo.binary)
total_used_bits += cost_con_num

# 建立矿车数量的辅助变量
truck_s = {}
for j in range(J):
    truck_s[f'truck{j}'] = kw.qubo.ndarray(to_binary(n[j]),f'truck{j}_s',kw.qubo.binary)
    total_used_bits += to_binary(n[j])
print('建立的变量总数为：',total_used_bits)
# 计算总成本表达式
total_cost_expression = kw.qubo.sum(
    kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) * costs[i]
    for i in range(len(costs)) if i in static_y)

cost_s_expression = kw.qubo.sum(cost_con_s[i] * (2**i) for i in range(cost_con_num))
# 构建成本约束
# budget_constraint = kw.qubo.constraint( (total_budget - total_cost_expression - cost_s_expression) ** 2, name = "budget")
qubo = QuboUtil()
budget_constraint = qubo.convert_qubo_constraint(total_budget - total_cost_expression - cost_s_expression, "budget")


# 分配的矿车数量小于矿车总数的约束
truck_constraints = {}
for j in range(J):
    truck_constraints[f'tru_con{j}'] = kw.qubo.constraint(
        (n[j] - kw.qubo.sum(kw.qubo.sum(k[f'k_{i}_{j}'][m] * (2**m) for m in range(len(k[f'k_{i}_{j}']))) for i in range(I) if f'k_{i}_{j}' in k)
            - kw.qubo.sum(truck_s[f'truck{j}'][m] * (2**m) for m in range(len(truck_s[f'truck{j}'])))) ** 2,name = f'tru_con{j}' )

# 计算zij的约束
zij_cons = {}
for i in range(I):
    if i not in static_y:
        continue
    for j in range(J):
        if m[i][j]==0 or k_val[f'k_{i}_{j}']==0:
            continue
        zij_cons[f'z{i}{j}'] = kw.qubo.constraint(
            (kw.qubo.sum( k[f'k_{i}_{j}'][m] * (2**m) for m in range( len(k[f'k_{i}_{j}']) ) ) + (zij[f'z_{i}_{j}']) - m[i][j] * 
             kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**m) for m in range(len(machine_vars[f'machine{i}']))))**2,
            name=f'zcons{i}{j}')


total_revenue = 160 * kw.qubo.sum(
    V[i] * R[i] * 20 * (kw.qubo.sum(machine_vars[f'machine{i}'][j] * (2**j) for j in range(len(machine_vars[f'machine{i}']))) - 0.5 * kw.qubo.sum(zij[f'z_{i}_{j}'] for j in range(J) if f'z_{i}_{j}' in zij))
    for i in range(I) if i in static_y
)*60 - 160 * 7 * kw.qubo.sum(
    C_oil_i[i] * kw.qubo.sum(get_generator(machine_vars[f'machine{i}'])) for i in range(I) if i in static_y
)*60 - 160 * 7 * kw.qubo.sum(
    C_oil_j[j] * kw.qubo.sum(get_generator(k[f'k_{i}_{j}'])) for i in range(I) for j in range(J) if f'k_{i}_{j}' in k
)*60 - kw.qubo.sum(
    C_ren_i[i] * kw.qubo.sum(get_generator(machine_vars[f'machine{i}'])) for i in range(I) if i in static_y
)*60 - kw.qubo.sum(
    C_wei_i[i] * kw.qubo.sum(get_generator(machine_vars[f'machine{i}'])) for i in range(I) if i in static_y
)*60 - kw.qubo.sum(
    C_ren_j[j] * kw.qubo.sum(get_generator(k[f'k_{i}_{j}'])) for i in range(I) if i in static_y for j in range(J)if f'k_{i}_{j}' in k
) * 60 - kw.qubo.sum(
    C_wei_j[j] * kw.qubo.sum(get_generator(k[f'k_{i}_{j}'])) for i in range(I) if i in static_y for j in range(J)if f'k_{i}_{j}' in k
) * 60 - kw.qubo.sum(
    C_cai[i] * kw.qubo.sum(get_generator(machine_vars[f'machine{i}'])) * 10000 for i in range(I) if i in static_y
)
get_generator_conditionally(machine_vars[f'machine{i}'], lambda x: x in static_y)


truck_cont_generator: Generator = (10000000 * truck_constraints[f'tru_con{j}'] for j in range(J))
obj = (-total_revenue + 10000000 * budget_constraint
    + kw.qubo.sum(truck_cont_generator)
       + kw.qubo.sum(1000*zij_cons[f'z{i}{j}'] for i in range(I) if i in static_y for j in range(J) if f'k_{i}_{j}' in k)
       )

obj = kw.qubo.make(obj)

obj_ising = kw.qubo.cim_ising_model(obj)

matrix = obj_ising.get_ising()["ising"]

# 使用 CIM 模拟器执行计算
output = kw.cim.simulator(
    matrix,
    pump=1.3,
    noise=0.3,
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
print(sol_dict)

obj_val = kw.qubo.get_val(obj, sol_dict)
objective_function_val = kw.qubo.get_val(total_revenue, sol_dict)
budget_constraint_val = kw.qubo.get_val(budget_constraint, sol_dict)
cost_con_val = qubo.read_num_from_dict(cost_con_s, sol_dict)
truck_constraints_val = {}
for j in range(3):
    truck_constraints_val[f'val{j}'] = kw.qubo.get_val(truck_constraints[f'tru_con{j}'], sol_dict)

zij_cons_val = {}
for i in range(4):
    if i in static_y:
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

print('矿车的分配数量：')
for k, v in k_values.items():
    print(f"{k}: {v}")

# 初始化总成本和总利润变量
total_cost = 0
total_profit = 0

# 遍历每种挖掘机
for i, (machine, quantity) in enumerate(machine_values.items()):
    if i in static_y:
        # 计算总成本
        total_cost += quantity * costs[i]


# 输出结果
print(f"总成本: {total_cost}")


# 检查是否超出预算
if total_cost > total_budget:
    print("超出预算！")
else:
    print("未超出预算。")
print(f'cost_con_val: {cost_con_val}')
print(f"obj Value: {obj_val}")
print(f"objective_function Value: {objective_function_val}")
print(f"budget_constraint Value: {budget_constraint_val}")

print(f"zij_cons Value: {zij_cons_val}")
# print(f"one_truck Value: {one_truck_val}")
print(f"truck_constraints Value: {truck_constraints_val}")

print("每种挖掘机的购买数量:")
for k, v in machine_values.items():
    print(f"{k}: {v}")