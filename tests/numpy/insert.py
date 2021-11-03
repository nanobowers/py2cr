import numpy as np

def aryfmt(i):
    if float("%.3f" % abs(i)) == 0:
        return "%.3f" % abs(i)
    return "%.3f" % i

def print_array(data):
    print(" ".join(list([aryfmt(i) for i in data])))

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

x = np.array([[1, 1], [2, 2], [3, 3]], dtype=np.int8)
"""[[1, 1], [2, 2], [3, 3]] => [1, 5, 1, 2, 2, 3, 3]"""
x = np.insert(x, 1, 5)
print_array(x)

x = np.array([[1, 1], [2, 2], [3, 3]])
"""[[1, 1], [2, 2], [3, 3]] => [[1, 5, 1], [2, 5, 2], [3, 5, 3]]"""
x = np.insert(x, 1, 5, axis=1)
print_matrix(x)
