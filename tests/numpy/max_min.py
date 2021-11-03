# coding: utf-8
import numpy as np

def print_array(data):
    print(" ".join(list(["%d" % i for i in data])))

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

x = np.array([2,3,4])
print_array(x)

z = np.array([[2,3,6],[3,4,5]])
print_matrix(z)

"""
max
"""
y = x.max()
print(y)
y = np.max([2, 3, 4])
print(y)

"""
amax
"""
y = np.amax([2, 3, 4])
print(y)

"""
max axis=0
"""
y = z.max(axis=0)
print_array(y)

"""
max axis=1
"""
y = np.max([[2,3,6],[3,4,5]], axis=1)
print_array(y)

"""
min
"""
y = x.min()
print(y)
y = np.min([2, 3, 4])
print(y)

"""
amin
"""
y = np.amin([2, 3, 4])
print(y)

"""
min axis=0
"""
y = z.min(axis=0)
print_array(y)

"""
min axis=1
"""
y = np.min([[2,3,6],[3,4,5]], axis=1)
print_array(y)

"""
max axis=0 keepdims
"""
y = np.max([[2,3,6],[3,4,5]], axis=0, keepdims=True)
print_matrix(y)

"""
min keepdims
"""
y = np.min([[2,3,6],[3,4,5]], keepdims=True)
print_matrix(y)
