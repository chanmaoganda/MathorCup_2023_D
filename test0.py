import pandas as pd
import kaiwu as kw
from math import log2, ceil

def to_bin(num):
    """
    计算整数变量需要转化成多少位二进制数的函数
    :param num: 十进制数
    :return: 二进制数
    """
    bin = int(ceil(log2(num + 1)))
    return bin


# 成本数据
costs = [100, 140, 200, 320]
total_budget = 1760
I = 4
# 矿车数量
J = 3
K = 3

# Placeholder parameters, replace with actual data
V = [0.9,1.2,0.8,2.1]  # Excavator bucket capacity
R =[190,175,165,150]  # Excavator operational efficiency
C_oil_i = [28,30,34,38] # Excavator oil consumption
C_cai = [100,140,300,320]  # Excavator procurement cost
C_ren_i = [7000,7500,8500,9000]  # Excavator labor cost
C_wei_i =[1000,1500,2000,3000]  # Excavator maintenance cost

C_oil_j = [18,22,27]  # Truck oil consumption
C_ren_j = [6000,7000,8000]  # Truck labor cost
C_wei_j =[2000,3000,4000]  # Truck maintenance cost

n = [7,7,3] # Number of trucks of type j
m = [[1,0,0],[2,1,0],[2,2,1],[0,2,1]]  # Excavator-truck requirements

# 定义记录变量数目的变量
cnt = 0

# 要买的挖掘机型号
static_y = [0,1,3]
# 对应的矿车型号
static_k = [0,1,2]

static_J = [0,1,2]

n = [6,6,2]


print(m[0][0], m[1][1], m[3][2])


minicost = 0;
for i in static_y:
    minicost += costs[i]
print(f'minicost: {minicost}')

total_budget = 2400

usedCosts = []
for i in static_y:
    usedCosts.append(costs[i])
print(f'usedcost: {usedCosts}')

# 为每种挖掘机计算最大购买数量
max_purchases = [(total_budget-minicost+cost)// cost for cost in usedCosts]
print(max_purchases)
# 计算表示每个数量所需的二进制变量数 xi所对应的ti的数量
bits_per_purchase = [to_bin(purchase) for purchase in max_purchases]
print(bits_per_purchase)


total_budget = 2400-minicost

# 计算需要添加的辅助变量的二进制位数
# bits_purchase_s = [int(ceil(log2(bits + 1))) for bits in bits_per_purchase]
# print("here is the value")
# print(bits_purchase_s)

# 对于每个挖掘机，创建购买数量的二进制变量 ti
machine_vars = {}
for i, n_bits in enumerate(bits_per_purchase):
    # 创建每种挖掘机所需数量的二进制变量 ti
    machine_vars[f'machine{static_y[i]}'] = kw.qubo.ndarray(n_bits, f"machine{static_y[i]}", kw.qubo.binary)
    cnt += n_bits
print(machine_vars)
print(machine_vars[f'machine{3}'][0])

# 创建k变量，表示i挖机分配的j矿车的数量
k = {}
zi = {}

print(len(static_y))

for i in range(len(static_y)):
    k[f'k_{static_y[i]}'] = kw.qubo.ndarray(to_bin(n[static_k[i]]), f'k_{static_y[i]}', kw.qubo.binary)
    zi[f'z_{static_y[i]}'] = kw.qubo.binary(f'z{static_y[i]}')
    cnt += (to_bin(n[static_k[i]]) + 1)

print('建立的zi为：',zi)

cost_con_num = int(ceil(log2(total_budget-minicost)))
cost_con_s = kw.qubo.ndarray(cost_con_num,'cost_con_s',kw.qubo.binary)
cnt += cost_con_num

# 建立矿车数量的辅助变量
truck_s = {}
for j in range(len(static_k)):
    truck_s[f'truck{static_k[j]}'] = kw.qubo.ndarray(to_bin(n[static_k[j]]),f'truck{static_k[j]}_s',kw.qubo.binary)
    cnt += to_bin(n[static_k[j]])
print('建立的变量总数为：',cnt)

# 计算总成本表达式
total_cost_expression = kw.qubo.sum(
    kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) * usedCosts[i]
    for i in range(len(usedCosts)))

cost_s_expression = kw.qubo.sum(cost_con_s[i] * (2**i) for i in range(cost_con_num))

# 构建成本约束
budget_constraint = kw.qubo.constraint((total_budget - total_cost_expression - cost_s_expression)**2, name="budget")

# 分配的矿车数量小于矿车总数的约束
truck_constraints = {}
for j in range(len(static_k)):
    truck_constraints[f'tru_con{static_k[j]}'] = (
        kw.qubo.constraint((n[static_k[j]]
                            - kw.qubo.sum(k[f'k_{static_y[j]}'][m] * (2 ** m) for m in range(len(k[f'k_{static_y[j]}'])))
                            - kw.qubo.sum(truck_s[f'truck{static_k[j]}'][m] * (2 ** m) for m in range(len(truck_s[f'truck{static_k[j]}'])))) ** 2,
                           name=f'tru_con{static_k[j]}'))


noUse_truck_constraints = {}
for j in range(len(static_k)):
    noUse_truck_constraints[f'tru_con{static_k[j]}'] = (
        kw.qubo.constraint(kw.qubo.sum(truck_s[f'truck{static_k[j]}'][m] * (2 ** m)
                                       for m in range(len(truck_s[f'truck{static_k[j]}']))) ** 2, name=f'tru_con{static_k[j]}'))

# 计算zi的约束
zi_cons = {}
for i in range(len(static_y)):
    zi_cons[f'z{static_y[i]}'] = kw.qubo.constraint((kw.qubo.sum(
        k[f'k_{static_y[i]}'][m1] * (2 ** m1) for m1 in range(len(k[f'k_{static_y[i]}'])))
                                           + (zi[f'z_{static_y[i]}'])
                                           - m[static_y[i]][static_k[i]] * kw.qubo.sum(
        machine_vars[f'machine{static_y[i]}'][m1] * (2 ** m1) for m1 in range(len(machine_vars[f'machine{static_y[i]}'])))) ** 2,
                                              name=f'zcons{static_y[i]}')



total_revenue = (
      160 * kw.qubo.sum(V[static_y[i]] * R[static_y[i]] * 20 * (kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) - 0.5 * zi[f'z_{static_y[i]}']) for i in range(len(static_y)))*60
    - 160 * kw.qubo.sum(C_oil_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
    - 160 * kw.qubo.sum(C_oil_j[static_k[i]] * kw.qubo.sum(k[f'k_{static_y[i]}'][m] * (2**m) for m in range(len(k[f'k_{static_y[i]}']))) for i in range(len(static_k)))*60
    - kw.qubo.sum(C_ren_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
    - kw.qubo.sum(C_wei_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
    - kw.qubo.sum(C_ren_j[static_k[i]] * kw.qubo.sum(k[f'k_{static_y[i]}'][m] * (2**m) for m in range(len(k[f'k_{static_y[i]}']))) for i in range(len(static_y))) * 60
    - kw.qubo.sum(C_wei_j[static_k[i]] * kw.qubo.sum(k[f'k_{static_y[i]}'][m] * (2**m) for m in range(len(k[f'k_{static_y[i]}']))) for i in range(len(static_y))) * 60
    - kw.qubo.sum(C_cai[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) * 10000 for i in range(len(static_y))))

obj = (-total_revenue + 1000000000*budget_constraint
    + kw.qubo.sum(300000000000*truck_constraints[f'tru_con{static_k[j]}'] for j in range(J))
    + kw.qubo.sum(400000000000*noUse_truck_constraints[f'tru_con{static_k[j]}'] for j in range(J))
    + kw.qubo.sum(10000000000*zi_cons[f'z{static_y[i]}'] for i in range(J)))

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

truck_constraints_val = {}
for j in range(3):
    truck_constraints_val[f'val{static_k[j]}'] = kw.qubo.get_val(truck_constraints[f'tru_con{static_k[j]}'], sol_dict)

zi_cons_val = {}
for i in range(3):
    zi_cons_val[f'z{static_y[i]}'] = kw.qubo.get_val(zi_cons[f'z{static_y[i]}'], sol_dict)

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

s_values = {}
for k, bits in truck_s.items():
    # 计算从二进制到整数的转换
    value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
    s_values[k] = value

# 输出结果
print('矿车的分配数量：')
for k, v in k_values.items():
    print(f"{k}: {v}")
print('没有使用的矿车数量：')
for k, v in s_values.items():
    print(f"{k}: {v}")

# 初始化总成本和总利润变量
total_cost = 0
total_profit = 0

# 遍历每种挖掘机
for i, (machine, quantity) in enumerate(machine_values.items()):
    # 计算总成本
    total_cost += quantity * costs[static_y[i]]
# 输出结果
print(f"总成本: {total_cost}")
# 检查是否超出预算
if total_cost > total_budget:
    print("超出预算！")
else:
    print("未超出预算。")

print(f"obj Value: {obj_val}")
print(f"objective_function Value: {objective_function_val}")
print(f"budget_constraint Value: {budget_constraint_val}")

print(f"zi_cons Value: {zi_cons_val}")
print(f"truck_constraints Value: {truck_constraints_val}")

print("每种挖掘机的购买数量:")
for k, v in machine_values.items():
    print(f"{k}: {v}")

# 有多少预算没有用完
x_val = kw.qubo.get_array_val(cost_con_s, sol_dict)
value = sum(x_val[j] * (2 ** j) for j, bit in enumerate(x_val))
print(x_val)
print(value)

zi_val = {}
for i in range(3):
    zi_val[f'z{static_y[i]}'] = kw.qubo.get_val(zi[f'z_{static_y[i]}'], sol_dict)
print(f"zi Value: {zi_val}")