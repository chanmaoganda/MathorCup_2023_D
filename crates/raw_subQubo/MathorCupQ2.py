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
et = [[1, 0, 0], [2, 1, 0], [2, 2, 1], [0, 2, 1]]  # Excavator-truck requirements

# 定义记录变量数目的变量

# 要买的挖掘机型号
# instance_maker = InstanceMaker()
# instances = instance_maker.make_all_instances()
# print(instances)

static_y = [0,1,3]

def func(static_y: list):
    cnt = 0
    # print(et[0][0], et[1][1], et[3][2])
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

    maxN = 0
    for i in n:
        if i> maxN:
            maxN = i
    print(f'maxN: {maxN}')

    max_purchasesNew = []
    for i in max_purchases:
        if i> maxN:
            max_purchasesNew.append(maxN)
        else:
            max_purchasesNew.append(i)
    print(max_purchasesNew)

    # 计算表示每个数量所需的二进制变量数 xi所对应的ti的数量
    bits_per_purchase = [to_bin(purchase) for purchase in max_purchasesNew]
    print(bits_per_purchase)

    # 对于每个挖掘机，创建购买数量的二进制变量 ti
    machine_vars = {}
    for i, n_bits in enumerate(bits_per_purchase):
        # 创建每种挖掘机所需数量的二进制变量 ti
        machine_vars[f'machine{static_y[i]}'] = kw.qubo.ndarray(n_bits, f"machine{static_y[i]}", kw.qubo.binary)
        cnt += n_bits
    print(machine_vars)

    kij = {}
    zij = {}
    print(len(static_y))

    for i in range(I):
        if i in static_y:
            for j in range(J):
                if et[i][j] != 0:
                    kij[f'k_{i}_{j}'] = kw.qubo.binary(f'k_{i}{j}')
                    zij[f'z_{i}_{j}'] = kw.qubo.binary(f'z_{i}{j}')
                    cnt += 1

    print('建立的kij为:', kij)
    print('建立的zi为:',zij)

    cost_con_num = int(ceil(log2(100)))
    cost_con_s = kw.qubo.ndarray(cost_con_num,'cost_con_s',kw.qubo.binary)
    cnt += cost_con_num

    # 计算总成本表达式
    total_cost_expression = kw.qubo.sum(
        kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) * usedCosts[i]
        for i in range(len(usedCosts)))

    cost_s_expression = kw.qubo.sum(cost_con_s[i] * (2**i) for i in range(cost_con_num))

    # 构建成本约束
    budget_constraint = kw.qubo.constraint((total_budget - total_cost_expression - cost_s_expression)**2, name="budget")

    # 每个挖机只分配一种矿车
    assign_truck_constraints = {}
    for i in range(len(static_y)):
        assign_truck_constraints[f'tru_con{static_y[i]}'] = (
            kw.qubo.constraint((kw.qubo.sum(kij[f'k_{static_y[i]}_{j}'] for j in range(J) if et[static_y[i]][j] != 0)-1) ** 2, name=f'tru_con{static_y[i]}'))

    # 每种矿车最多只分配一类挖机
    truck_constraints = {}
    for j in range(J):
        truck_constraints[f'tru2_con{j}'] = (
            kw.qubo.constraint(
                (kw.qubo.sum(kij[f'k_{static_y[i]}_{j}'] for i in range(len(static_y)) if et[static_y[i]][j] != 0) - 1) ** 2,
                name=f'tru2_con{j}'))

    # 计算zi的约束
    zi_cons = {}
    for i in range(len(static_y)):
        for h in range(J):
            if et[static_y[i]][h] != 0:
                zi_cons[f'z{static_y[i]}_{h}'] = kw.qubo.constraint(
                (kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}'])))
                        * kij[f'k_{static_y[i]}_{h}'] * et[static_y[i]][h]
                        + (zij[f'z_{static_y[i]}_{h}'])
                        - kij[f'k_{static_y[i]}_{h}'] * n[h]) ** 2, name=f'zcons{static_y[i]}_{h}')

    C_oil_j0 = kw.qubo.sum(kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}'])))
                              * kw.qubo.sum(C_oil_j[h] * kij[f'k_{static_y[i]}_{h}']*et[static_y[i]][h] for h in range(J) if et[static_y[i]][h] != 0) 
                              for i in range(len(static_y)))

    C_oil_j1 = kw.qubo.sum(kw.qubo.sum(C_oil_j[h] * zij[f'z_{static_y[i]}_{h}'] for h in range(J) if et[static_y[i]][h]!= 0) for i in range(len(static_y)))

    C_renwei_j0 = kw.qubo.sum(kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2 ** j) for j in range(len(machine_vars[f'machine{static_y[i]}'])))
                           * kw.qubo.sum(C_oil_j[h] * kij[f'k_{static_y[i]}_{h}'] * et[static_y[i]][h] for h in range(J) if f'k_{static_y[i]}_{h}' in kij) for i in range(len(static_y)))
    C_renwei_j1 = kw.qubo.sum(kw.qubo.sum(C_oil_j[h] * zij[f'z_{static_y[i]}_{h}'] for h in range(J) if f'k_{static_y[i]}_{h}' in kij) for i in range(len(static_y)))

    total_revenue = (
          160 * kw.qubo.sum(V[static_y[i]] * R[static_y[i]] * 20 * (kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}'])))
                                                                    - 0.5 * kw.qubo.sum(zij[f'z_{static_y[i]}_{h}'] for h in range(J) if f'k_{static_y[i]}_{h}' in kij)) for i in range(len(static_y)))*60
        - 160 * kw.qubo.sum(C_oil_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
        - 160 * (C_oil_j0 - C_oil_j1) *60
        - kw.qubo.sum(C_ren_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
        - kw.qubo.sum(C_wei_i[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) for i in range(len(static_y)))*60
        - (C_renwei_j0-C_renwei_j1) * 60
        - kw.qubo.sum(C_cai[static_y[i]] * kw.qubo.sum(machine_vars[f'machine{static_y[i]}'][j] * (2**j) for j in range(len(machine_vars[f'machine{static_y[i]}']))) * 10000 for i in range(len(static_y)))
    )

    obj = (-total_revenue + 30000000000*budget_constraint
        + kw.qubo.sum(1000000000*assign_truck_constraints[f'tru_con{static_y[i]}'] for i in range(J))
        + kw.qubo.sum(100000000000*truck_constraints[f'tru2_con{j}'] for j in range(J))
        # + kw.qubo.sum(100000000000*kw.qubo.sum(zi_cons[f'z{static_y[i]}_{h}'] for h in range(J) if et[static_y[i]][h] != 0) for i in range(J))
           )

    obj = kw.qubo.make(obj)
    obj_ising = kw.qubo.cim_ising_model(obj)
    matrix = obj_ising.get_ising()["ising"]

    # 使用 CIM 模拟器执行计算
    output = kw.cim.simulator(
        matrix,
        pump=1.3,
        noise=0.3,
        laps=8000,
        dt=0.1,
        normalization=1.2,
        iterations=100)

    # 对结果进行排序并选择最佳解
    opt = kw.sampler.optimal_sampler(matrix, output, bias=0, negtail_ff=False)

    globalObj = 0
    globalwc = []
    globalzi = []
    globalkc = []
    globalwk = []

    count = 0
    for sol in opt[0]:
        cim_sol = sol * sol[-1]
        variables = obj_ising.get_variables()
        # Substitute the spin vector and obtain the result dictionary
        sol_dict0 = kw.qubo.get_sol_dict(cim_sol, variables)
        # print(sol_dict0)

        obj_val = kw.qubo.get_val(obj, sol_dict0)
        objective_function_val = kw.qubo.get_val(total_revenue, sol_dict0)
        budget_constraint_val = kw.qubo.get_val(budget_constraint, sol_dict0)

        # 从QUBO解中获取每种挖掘机的数量
        solInfea = False
        solutionInfeasible = 0
        machine_values = {}
        for machine, bits in machine_vars.items():
            # 计算从二进制到整数的转换
            value = sum(kw.qubo.get_val(bit, sol_dict0) * (2 ** j) for j, bit in enumerate(bits))
            machine_values[machine] = value
            if value == 0:
                print("挖掘机数量为零！")
                solutionInfeasible = 1
                break

        if solutionInfeasible == 1:
            continue

        # 遍历每种挖掘机
        total_cost = 0
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
            real_obj = 0
            ct = 0
            wc = []
            kc = []
            zii = []
            for i, v in machine_values.items():
                wc.append(v)
                # print(f"{i}: {v}")

            if wc == [7,7,2]:
                print(wc)
                print('挖机和矿车匹配关系：')
                for k, v in kij.items():
                    print(f"{k}: {v}: {kw.qubo.get_val(v, sol_dict0)}")

            zi_cons_val = {}
            kij_cons_val = {}
            kij_cons_val1 = {}
            for i in range(3):
                kij_cons_val[f'tru_con{static_y[i]}'] = kw.qubo.get_val(
                    assign_truck_constraints[f'tru_con{static_y[i]}'], sol_dict0)
                for j in range(J):
                    if et[static_y[i]][j] != 0:
                        zi_cons_val[f'z{static_y[i]}_{j}'] = kw.qubo.get_val(zi_cons[f'z{static_y[i]}_{j}'],
                                                                             sol_dict0)

            for j in range(J):
                kij_cons_val1[f'tru2_con{j}'] = kw.qubo.get_val(truck_constraints[f'tru2_con{j}'], sol_dict0)

            print(f"truck_constraints Value1: {kij_cons_val}")
            print(f"truck_constraints Value2: {kij_cons_val1}")

            constraintViolate = False
            for f1, bits in kij_cons_val.items():
                if int(bits) == 1:
                    constraintViolate = True
                    break

            if constraintViolate == False:
                for f1, bits in kij_cons_val1.items():
                    if int(bits) == 1:
                        constraintViolate = True
                        break

            if constraintViolate == False:
                print(f"start to recalculate the objective")
                for k, v in kij.items():
                    print(f"{k}: {v}: {kw.qubo.get_val(v, sol_dict0)}")

                wk = []
                for i in range(I):
                    if i in static_y:
                        for j in range(J):
                            if et[i][j] != 0:
                                if int(kw.qubo.get_val(kij[f'k_{i}_{j}'], sol_dict0)) == 1:
                                    wk.append(j)

                print(f"===================================================={wk}")

                real_obj, realwc, realkc, realzii = getSolution(wk, machine_values)

                if real_obj > globalObj:
                    globalObj = real_obj
                    globalwc = realwc
                    globalzi = realzii
                    globalkc = realkc
                    globalwk = wk

        count += 1
        if count > 1000:
            break

    print(f"===========================================")
    print(globalObj)
    print(globalwc)
    print(globalzi)
    print(globalkc)
    print(globalwk)

    best = opt[0][0]
    # If the linear term variable is -1, perform a flip
    cim_best = best * best[-1]
    # Get the list of variable names
    vars = obj_ising.get_variables()
    # Substitute the spin vector and obtain the result dictionary
    sol_dict = kw.qubo.get_sol_dict(cim_best, vars)
    # print(f"number of solution {count}")
    print(sol_dict)

    obj_val = kw.qubo.get_val(obj, sol_dict)
    objective_function_val = kw.qubo.get_val(total_revenue, sol_dict)
    budget_constraint_val = kw.qubo.get_val(budget_constraint, sol_dict)
    
    zi_cons_val = {}
    kij_cons_val = {}
    kij_cons_val1 = {}
    for i in range(3):
        kij_cons_val[f'tru_con{static_y[i]}'] = kw.qubo.get_val(assign_truck_constraints[f'tru_con{static_y[i]}'], sol_dict)
        for j in range(J):
            if et[static_y[i]][j]!= 0:
                zi_cons_val[f'z{static_y[i]}_{j}'] = kw.qubo.get_val(zi_cons[f'z{static_y[i]}_{j}'], sol_dict)

    for j in range(J):
        kij_cons_val1[f'tru2_con{j}'] = kw.qubo.get_val(truck_constraints[f'tru2_con{j}'], sol_dict)


    # 从QUBO解中获取每种挖掘机的数量
    machine_values = {}
    for machine, bits in machine_vars.items():
        # 计算从二进制到整数的转换
        value = sum(kw.qubo.get_val(bit, sol_dict) * (2 ** j) for j, bit in enumerate(bits))
        machine_values[machine] = value

    print('挖机和矿车匹配关系：')
    for k, v in kij.items():
        print(f"{k}: {v}: {kw.qubo.get_val(v, sol_dict)}")

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
    print(f"truck_constraints Value1: {kij_cons_val}")
    print(f"truck_constraints Value2: {kij_cons_val1}")

    print("每种挖掘机的购买数量:")
    for k, v in machine_values.items():
        print(f"{k}: {v}")

    # 有多少预算没有用完
    x_val = kw.qubo.get_array_val(cost_con_s, sol_dict)
    value = sum(x_val[j] * (2 ** j) for j, bit in enumerate(x_val))
    print(x_val)
    print(value)
    print()

    wk = []
    for i in range(I):
        if i in static_y:
            for j in range(J):
                if et[i][j] != 0:
                    if int(kw.qubo.get_val(kij[f'k_{i}_{j}'], sol_dict)) == 1:
                        wk.append(j)

    realObjvalue, realWC, realKC, realzi = getSolution(wk, machine_values)
    print(realObjvalue)
    print(realWC)
    print(realKC)
    print(realzi)

def getSolution(static_k, machine_values):
    real_obj = 0
    ct = 0
    wc = []
    kc = []
    zii = []
    for i, v in machine_values.items():
        print(f"{i}: {v}")
        # print(static_y[ct])
        if v * et[static_y[ct]][static_k[ct]] > n[static_k[ct]]:
            kc.append(n[static_k[ct]])
            if (n[static_k[ct]] % et[static_y[ct]][static_k[ct]]) == 1:
                wc.append(n[static_k[ct]] // et[static_y[ct]][static_k[ct]] + 1)
                zii.append(1)
            else:
                wc.append(n[static_k[ct]] // et[static_y[ct]][static_k[ct]])
                zii.append(0)
        else:
            kc.append(v * et[static_y[ct]][static_k[ct]])
            zii.append(0)
            wc.append(v)
        ct += 1
    print(wc)
    print(zii)
    print(kc)
    ct = 0
    for v in wc:
        real_obj += 160 * V[static_y[ct]] * R[static_y[ct]] * 20 * v * 60
        real_obj -= 160 * C_oil_i[static_y[ct]] * v * 60
        real_obj -= C_ren_i[static_y[ct]] * v * 60
        real_obj -= C_wei_i[static_y[ct]] * v * 60
        real_obj -= C_cai[static_y[ct]] * v * 10000
        ct += 1
    ct = 0
    for v in zii:
        real_obj -= 160 * V[static_y[ct]] * R[static_y[ct]] * 20 * 0.5 * v * 60
        ct += 1
    ct = 0
    for v in kc:
        print(f"矿车数量: {v}")
        real_obj -= 160 * C_oil_j[static_k[ct]] * v * 60
        real_obj -= C_ren_j[static_k[ct]] * v * 60
        real_obj -= C_wei_j[static_k[ct]] * v * 60
        ct += 1
    print(real_obj)
    print(wc)
    print(kc)
    print('==============')
    return real_obj, wc, kc, zii


func(static_y)

