from SubQuboSolver import SubQuboSolver
from Instance import Instance

instance = Instance([0, 1, 3], [0, 1, 2])

sub_qubo_solver = SubQuboSolver(instance)

sub_qubo_solver.solve()
