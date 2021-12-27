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

def edmond_solve(data):
    N, D, d, max_d, c = data['N'], data['D'], data['d'], data['max_d'], data['c']
    V = set()
    E = set()
    r = 0
    w = dict()
    t = dict()
    s = ''
    total_cost = 0
    for i in range(N):
        V.add(i)
        for j in range(N):
            if j!=i:
                E.add((i,j))
                w[(i,j)] = c[i][j]
                t[(i,j)] = d[i][j]
    result = msa(V, E, r, w, t, D)
    for edge in result:
        print("%d -> %d : %d\n"%(edge[0], edge[1],c[edge[0]][edge[1]]))
        s += "%d -> %d\n"%(edge[0], edge[1])
        total_cost += c[edge[0]][edge[1]] 
    s += "Cost: %8.3f\n"%(total_cost)
    print(total_cost)
    return s
def msa(V, E, r, w, t, D):
    """
    Recursive Edmond's algorithm as per Wikipedia's explanation
    Returns a set of all the edges of the minimum spanning arborescence.
    V := set( Vertex(v) )
    E := set( Edge(u,v) )
    r := Root(v)
    w := dict( Edge(u,v) : cost)
    t := dict( Edge(u,v) : time)
    D := max of total time in each path
    """

    """
    Step 1 : Removing all edges that lead back to the root
    """
    for (u,v) in E.copy():
        if v == r:
            E.remove((u,v))
            w.pop((u,v))

    """
    Step 2 : Finding the minimum incoming edge for every vertex. O(n**2) but okay since it is
    a small sized list
    """
    pi = dict()
    for v in V:
        edges = [edge[0] for edge in E if edge[1] == v]
        if not len(edges):
            continue
        costs = [w[(u,v)] for u in edges]
        pi[v] = edges[costs.index(min(costs))]
    
    """
    Step 3 : Finding cycles and over load path in the graph
    """
    cycle_vertex = None
    over_load_path_vertex = None
    for v in V:
        if cycle_vertex is not None:
            break
        visited = set()
        next_v = pi.get(v)
        while next_v:
            if next_v in visited:
                cycle_vertex = next_v
                break
            visited.add(next_v)
            next_v = pi.get(next_v)
    
    if cycle_vertex is None:
        for v in V:
            if over_load_path_vertex is not None:
                break
            total_time = 0
            next_v = pi.get(v)
            while next_v:
                if total_time > D:
                    over_load_path_vertex = next_v
                    break
                total_time += t[(next_v,v)]
                next_v = pi.get(next_v)

    """
    Step 4 : If there is no cycle or over load path, return all the minimum edges pi(v)
    """
    if cycle_vertex is None and over_load_path_vertex is None:
        return set([(pi[v],v) for v in pi.keys()])
    
    """
    Step 5 : if there is a cycle, all the vertices in the cycle must be identified
    """
    if cycle_vertex is not None:
        C = set()
        C.add(cycle_vertex)
        next_v = pi.get(cycle_vertex)
        while next_v != cycle_vertex:
            C.add(next_v)
            next_v = pi.get(next_v)

        v_c = -cycle_vertex**2
        V_prime = set([v for v in V if v not in C] + [v_c])
        E_prime = set()
        w_prime = dict()
        t_prime = dict()
        correspondence = dict()
        for (u,v) in E:
            if u not in C and v in C:
                e = (u,v_c)
                if e in E_prime:
                    if w_prime[e] < w[(u,v)] - w[(pi[v],v)]:
                        continue
                w_prime[e] = w[(u,v)] - w[(pi[v],v)]
                t_prime[e] = t[(u,v)] - t[(pi[v],v)]
                correspondence[e] = (u,v)
                E_prime.add(e)
            elif u in C and v not in C:
                e = (v_c,v)
                if e in E_prime:
                    old_u = correspondence[e][0]
                    if w[(old_u,v)] < w[(u,v)]:
                        continue
                E_prime.add(e)
                w_prime[e] = w[(u,v)]
                t_prime[e] = t[(u,v)]
                correspondence[e] = (u,v)
            elif u not in C and v not in C:
                e = (u,v)
                E_prime.add(e)
                w_prime[e] = w[(u,v)]
                t_prime[e] = t[(u,v)]
                correspondence[e] = (u,v)

    elif over_load_path_vertex is not None:
        C = set()
        C.add(over_load_path_vertex)
        next_v = pi.get(over_load_path_vertex)
        while next_v != 0:
            C.add(next_v)
            next_v = pi.get(next_v)

        v_c = -over_load_path_vertex**2
        V_prime = set([v for v in V if v not in C] + [v_c])
        E_prime = set()
        w_prime = dict()
        t_prime = dict()
        correspondence = dict()
        for (u,v) in E:
            if u not in C and v in C:
                e = (u,v_c)
                if e in E_prime:
                    if w_prime[e] < w[(u,v)] - w[(pi[v],v)]:
                        continue
                w_prime[e] = w[(u,v)] - w[(pi[v],v)]
                t_prime[e] = t[(u,v)] - t[(pi[v],v)]
                correspondence[e] = (u,v)
                E_prime.add(e)
            elif u in C and v not in C:
                e = (v_c,v)
                if e in E_prime:
                    old_u = correspondence[e][0]
                    if w[(old_u,v)] < w[(u,v)]:
                        continue
                E_prime.add(e)
                w_prime[e] = w[(u,v)]
                t_prime[e] = t[(u,v)]
                correspondence[e] = (u,v)
            elif u not in C and v not in C:
                e = (u,v)
                E_prime.add(e)
                w_prime[e] = w[(u,v)]
                t_prime[e] = t[(u,v)]
                correspondence[e] = (u,v)
                
    tree = msa(V_prime, E_prime, r, w_prime, t_prime, D)

    """
    Step 6 : 
    """
    cycle_edge = None
    for (u,v) in tree:
        if v == v_c:
            old_v = correspondence[(u,v_c)][1]
            cycle_edge = (pi[old_v],old_v)
            break
    
    ret = set([correspondence[(u,v)] for (u,v) in tree])
    for v in C:
        u = pi[v]
        ret.add((u,v))
        
    ret.remove(cycle_edge)
    
    return ret

if __name__ == '__main__':
    file_name = 'data1000.txt'
    data = read_data(file_name)
    # print(data['N'])
    start = time.time()
    s = edmond_solve(data)
    stop = time.time()
    s += "Solving time: %8.3f"%(stop - start)
    output_file_name = file_name.replace('data', 'output_edmond')
    with open(os.path.abspath(os.path.join(os.curdir, 'Edmond_solution', 'output', output_file_name)), 'w', encoding='utf-8') as f:
        f.write(s)