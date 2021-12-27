from ortools.sat.python import cp_model
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

def cp_solve(data):
    N, D, d, max_d, c = data['N'], data['D'], data['d'], data['max_d'], data['c']
    model = cp_model.CpModel()

    x = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i == j:
                continue
            elif j == 0:
                x[i, j] = model.NewIntVar(0, 0, "x[%d, %d]"%(i, j))
            else:
                x[i, j] = model.NewBoolVar("x[%d, %d]"%(i, j))
    
    t = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i == j:
                continue
            if i == 0:
                t[i, j] = model.NewIntVar(1, 1, "t[%d, %d]"%(i, j))
            elif j == 0:
                t[i, j] = model.NewIntVar(0, 0, "t[%d, %d]"%(i, j))
            else:
                t[i, j] = model.NewBoolVar("t[%d, %d]"%(i, j))

    z = dict()
    for i in range(0, N):
        z[i] = model.NewIntVar(0, D, "z[%d]"%(i))

    ct1 = dict()
    for i in range(1, N):
        ct1[i] = model.Add(sum(x[j, i] for j in range(0, N) if i != j) == 1)
    
    ct2 = dict()
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                ct2[i, j] = model.Add(z[j] - z[i] + (-d[i][j] + max_d * (1 - N)) * x[i, j] >= max_d * (1 - N))

    ct3 = dict()
    for i in range(1, N):
        for j in range(1, N):
            if i == j:
                continue
            else:
                ct3[i, j] = model.Add(t[i, j] == 1).OnlyEnforceIf(x[i, j])

    ct4 = dict()
    for i in range(0, N):
        for j in range(i + 1, N):
            ct4[i, j] = model.Add(t[i, j] + t[j, i] <= 1)
    
    ct5 = dict()
    for i in range(1, N):
        for j in range(1, N):
            for k in range(1, N):
                if i != j and j != k and k != i:
                    ct5[i, j, k] = model.Add(t[i, k] == 1).OnlyEnforceIf([t[i, j], t[j, k]])

    model.Minimize(sum(c[i][j] * x[i, j] for i in range(0, N) for j in range(0, N) if i != j))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 3600.0
    status = solver.Solve(model)
    s = ''
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for i in range(0, N):
            for j in range(0, N):
                if i != j and solver.Value(x[i, j]) == 1:
                    s += "%d -> %d\n"%(i, j)
        s += "Cost: %8.3f\n"%(solver.ObjectiveValue())
    else:
        s += "No optimal solution!\n"
    return s



if __name__ == '__main__':
    file_name = 'data3.txt'
    data = read_data(file_name)
    print(file_name)
    start = time.time()
    s = cp_solve(data)
    stop = time.time()
    s += "Solving time: %8.3f"%(stop - start)
    output_file_name = file_name.replace('data', 'output')
    with open(os.path.abspath(os.path.join(os.curdir, 'CP', 'output', output_file_name)), 'w', encoding='utf-8') as f:
        f.write(s)
    