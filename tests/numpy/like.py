# coding: utf-8
import numpy as np

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

x = np.arange(6)
x = x.reshape(2, 3)
print_matrix(x)

x = np.ones_like(x)
print_matrix(x)

x = np.zeros_like(x)
print_matrix(x)

x = np.full_like(x, 1)
print_matrix(x)

a = ([1,2,3], [4,5,6])   
x = np.empty_like(a)
print(list(x.shape))

a = np.array([[1., 2., 3.],[4.,5.,6.]])
x = np.empty_like(a)
print(list(x.shape))
