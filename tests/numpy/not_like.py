# coding: utf-8
import numpy as np

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

def aryfmt(i):
    if float("%.3f" % abs(i)) == 0:
        return "%.3f" % abs(i)
    return "%.3f" % i
def print_array(data):
    print(" ".join(list([aryfmt(i) for i in data])))
    

x1 = np.ones(5, dtype=np.int8)
print_array(x1)

x2 = np.ones(5)
print_array(x2)

x3 = np.zeros(5)
print_array(x3)

# TODO: temporarily unsupported

#x4 = np.full((2, 2), 1)
#print_matrix(x4)

#x5 = np.empty([2, 2])
#print(list(x5.shape))


