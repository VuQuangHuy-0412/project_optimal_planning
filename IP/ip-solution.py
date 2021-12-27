from ortools.linear_solver import pywraplp
import os
import time

def read_data(file_name):
    data_dir = 'DataSet'
    with open(os.path.abspath(os.path.join(data_dir, file_name)), 'r') as f:
        lines = f.readlines()

    data = dict()
    data['N'], data['D'] = (int(e) for e in lines[0].split(' '))

    data['d'] = list()
    for line in lines[1:data['N'] + 1]:
        data['d'].append([int(e) for e in line.split(' ')][:data['N']])
    data['max_d'] = max([v for u in data['d'] for v in u])

    data['c'] = list()
    for line in lines[data['N'] + 1:2 * data['N'] + 1]:
        data['c'].append([int(e) for e in line.split(' ')][:data['N']])
    return data

def ip_solve(data):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    N, D, d, max_d, c = data['N'], data['D'], data['d'], data['max_d'], data['c']

    x = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i == j:
                continue
            elif j == 0:
                x[i, j] = solver.IntVar(0, 0, "x[%d, %d]"%(i, j))
            else:
                x[i, j] = solver.IntVar(0, 1, "x[%d, %d]"%(i, j))

    y = dict()
    for i in range(0, N):
        if i == 0:
            y[i] = solver.IntVar(0, 0, "y[%d]"%(i))
        else:
            y[i] = solver.IntVar(1, N - 1, "y[%d]"%(i))
    
    z = dict()
    for i in range(0, N):
        z[i] = solver.IntVar(0, D, "z[%d]"%(i))

    ct1 = dict()
    for i in range(1, N):
        ct1[i] = solver.Constraint(1, 1, "ct1[%d]"%(i))
        for j in range(0, N):
            if i != j:
                ct1[i].SetCoefficient(x[j, i], 1)
    
    ct2 = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                ct2[i, j] = solver.Constraint(1 - N, solver.infinity(), "ct2[%d, %d]"%(i, j))
                ct2[i, j].SetCoefficient(y[j], 1)
                ct2[i, j].SetCoefficient(y[i], -1)
                ct2[i, j].SetCoefficient(x[i, j], -N)
    
    ct3 = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                ct3[i, j] = solver.Constraint(max_d * (1 - N), solver.infinity(), "ct3[%d, %d]"%(i, j))
                ct3[i, j].SetCoefficient(z[j], 1)
                ct3[i, j].SetCoefficient(z[i], -1)
                ct3[i, j].SetCoefficient(x[i, j], -d[i][j] + max_d * (1 - N))

    objective = solver.Objective()
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                objective.SetCoefficient(x[i, j], c[i][j])
    objective.SetMinimization()

    # print(solver.ExportModelAsLpFormat(False).replace('\\', '').replace(',_', ','), sep='\n')
    # solver.parameters.max_time_in_seconds = 3600.0
    solver.SetTimeLimit(3600000)
    status = solver.Solve()
    # print("Status", status)
    s = ''
    if status in [pywraplp.Solver.FEASIBLE, pywraplp.Solver.OPTIMAL]:
        for i in range(0, N):
            for j in range(0, N):
                if i != j and x[i, j].solution_value() == 1:
                    s += "%d -> %d\n"%(i, j)
        s += "Cost: %8.3f\n"%(objective.Value())
    else:
        s += "No optimal solution!\n"
    return s


if __name__ == '__main__':
    file_name = 'data3.txt'
    data = read_data(file_name)
    print(file_name)
    start = time.time()
    s = ip_solve(data)
    stop = time.time()
    s += "Solving time: %8.3f"%(stop - start)
    output_file_name = file_name.replace('data', 'output')
    with open(os.path.abspath(os.path.join(os.curdir, 'IP', 'output', output_file_name)), 'w', encoding='utf-8') as f:
        f.write(s)
