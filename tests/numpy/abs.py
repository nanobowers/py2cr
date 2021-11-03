# coding: utf-8
import numpy as np

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

def print_array(data):
    print(" ".join(list(["%d" % i for i in data])))

"""
1-dim
"""
x = np.array([2,-3,4])
print_array(x)

y = np.abs(x)
print_array(y)

y = np.absolute(x)
print_array(y)
"""
2-dim
"""
z = np.array([[-2,3,-6],[3,-4,5]])
print_matrix(z)

y = np.abs(z)
print_matrix(y)

