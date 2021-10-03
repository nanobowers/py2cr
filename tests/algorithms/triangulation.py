def abs(x):
    if x > 0:
        return x
    else:
        return -x

def sqrt(x):
    eps = 1e-10
    x = float(x)
    r = x/2
    residual = r**2 - x
    while abs(residual) > eps:
        r_d = -residual/(2*r)
        r += r_d
        residual = r**2 - x
    return r

def is_on_the_left(c, a, b, pts_list):
   ax, ay = pts_list[a]
   bx, by = pts_list[b]
   cx, cy = pts_list[c]
   ux = float(bx - ax)
   uy = float(by - ay)
   vx = float(cx - ax)
   vy = float(cy - ay)
   return (ux*vy - uy*vx > 0)

def criterion(a, b, c, pts_list):
   ax, ay = pts_list[a]
   bx, by = pts_list[b]
   cx, cy = pts_list[c]
   ux = float(ax - cx)
   uy = float(ay - cy)
   vx = float(bx - cx)
   vy = float(by - cy)
   len_u = sqrt(ux*ux + uy*uy)
   len_v = sqrt(vx*vx + vy*vy)
   return (ux*vx + uy*vy)/(len_u*len_v)

def find_third_point(a, b, pts_list, edges):
    """
    Take a boundary edge (a,b), and in the list of points
    find a point 'c' that lies on the left of ab and maximizes
    the angle acb
    """
    found = 0
    minimum = 10**8   #this is dirty
    c_index = -1
    pt_index = -1
    for c_point in pts_list:
        c_index += 1
        if c_index != a and c_index != b and is_on_the_left(c_index, a, b, pts_list):
            edge_intersects = \
                    edge_intersects_edges((a, c_index), pts_list, edges) or \
                    edge_intersects_edges((b, c_index), pts_list, edges)
            if not edge_intersects:
                crit = criterion(a, b, c_index, pts_list)
                if crit < minimum:
                    minimum = crit
                    pt_index = c_index
                    found = 1
    if found == 0:
        raise TriangulationError("ERROR: Optimal point not found in find_third_point().")
    return pt_index

def lies_inside(c, bdy_edges):
   for edge in bdy_edges:
       a,b = edge
       if c == a or c == b: return False
   return True

def is_boundary_edge(a, b, bdy_edges):
    """
    Checks whether edge (a, b) is in the list of boundary edges
    """
    for edge in bdy_edges:
        a0, b0 = edge
        if a == a0 and b == b0:
            return True
    return False

def triangulate_af(pts_list, bdy_edges):
    """
    Create a triangulation using the advancing front method.
    """
    # create empty list of elements
    elems = []
    bdy_edges = bdy_edges[:]
    # main loop
    while bdy_edges != []:
        # take the last item from the list of bdy edges (and remove it)
        a,b = bdy_edges.pop()
        c = find_third_point(a, b, pts_list, bdy_edges)
        elems.append((a,b,c))
        if is_boundary_edge(c, a, bdy_edges):
            bdy_edges.remove((c,a))
        else:
            bdy_edges.append((a,c))
        if is_boundary_edge(b, c, bdy_edges):
            bdy_edges.remove((b,c))
        else:
            bdy_edges.append((c,b))
    return elems

def ccw(a, b, c):
    return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])

def intersect(a, b, c, d):
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)

def two_edges_intersect(nodes, e1, e2):
    """
    Checks whether the two edges intersect.

    It assumes that e1 and e2 are tuples of (a_id, b_id) of ids into the nodes.
    """
    a = nodes[e1[0]]
    b = nodes[e1[1]]
    c = nodes[e2[0]]
    d = nodes[e2[1]]
    return intersect(a, b, c, d)

def any_edges_intersect(nodes, edges):
    """
    Returns True if any two edges intersect.
    """
    for i in range(len(edges)):
        for j in range(i+1, len(edges)):
            e1 = edges[i]
            e2 = edges[j]
            if e1[1] == e2[0] or e1[0] == e2[1]:
                continue
            if two_edges_intersect(nodes, e1, e2):
                return True
    return False

def edge_intersects_edges(e1, nodes, edges):
    """
    Returns True if "e1" intersects any edge from "edges".
    """
    for i in range(len(edges)):
        e2 = edges[i]
        if e1[1] == e2[0] or e1[0] == e2[1]:
            continue
        if two_edges_intersect(nodes, e1, e2):
            return True
    return False

def example1():
    nodes = [
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1),
            ]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    elems = triangulate_af(nodes, edges)
    return nodes, edges, elems

def example2():
    nodes = [
            (0, 0),
            (1, 0),
            (2, 1),
            (2, 2),
            (1, 2),
            (0.5, 1.5),
            (0, 1),
            ]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    elems = triangulate_af(nodes, edges)
    return nodes, edges, elems

nodes, edges, elems = example1()
print("nodes", nodes)
print("edges", edges)
print("elems", elems)
if not any_edges_intersect(nodes, edges):
    print("ok")

print()
nodes, edges, elems = example2()
print("nodes", nodes)
print("edges", edges)
print("elems", elems)
if not any_edges_intersect(nodes, edges):
    print("ok")
