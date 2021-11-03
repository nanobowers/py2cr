# coding: utf-8
import numpy as np

def print_array(data):
    print(" ".join(list(["%d" % i for i in data])))

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

a = np.asarray([[1,2,3],[4,5,6]])
print_matrix(a)

x = np.argmax(a)
print(x)

"""
<Not Compatible with axis>
Python argmax  : [1, 1, 1]
Ruby max_index : [3, 4, 5] (flat Array index)
"""
x = np.argmax(a, axis=0)
print_array(x)

"""
<Not Compatible with axis>
Python argmax  : [2, 2]
Ruby max_index : [2, 5] (flat Array index)
 """
x = np.argmax(a, axis=1)
print_array(x)

x = np.argmin(a)
print(x)

"""
<Not Compatible with axis>
Python argmax  : [0, 0, 0]
Ruby max_index : [0, 1, 2] (flat Array index)
 """
x = np.argmin(a, axis=0)
print_array(x)

"""
<Not Compatible with axis>
Python argmax  : [0, 0]
Ruby max_index : [0, 3] (flat Array index)
 """
x = np.argmin(a, axis=1)
print_array(x)

