
class Variables:
    def __init__(self, n, et, V, R, C_oil_i, C_cai, C_ren_i, C_wei_i, C_oil_j, C_ren_j, C_wei_j, static_y, total_budget, costs):
        self.n = n
        self.et = et
        self.V = V
        self.R = R
        self.C_oil_i = C_oil_i
        self.C_cai = C_cai
        self.C_ren_i = C_ren_i
        self.C_wei_i = C_wei_i
        self.C_oil_j = C_oil_j
        self.C_ren_j = C_ren_j
        self.C_wei_j = C_wei_j
        self.static_y = static_y
        self.I = len(static_y)
        self.J = len(n)
        self.total_budget = total_budget
        self.costs = costs