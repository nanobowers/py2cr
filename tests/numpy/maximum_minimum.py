# coding: utf-8
import numpy as np

def aryfmt(i):
    if float("%.3f" % abs(i)) == 0:
        return "%.3f" % abs(i)
    return "%.3f" % i
def print_array(data):
    print(" ".join(list([aryfmt(i) for i in data])))

x = np.arange(-5.0, 5.0, 0.1)
print(len(x))
print_array(list(x))

"""
maximum
"""
y = np.maximum(0, x)
print(len(y))
print_array(list(y))

"""
minimum
"""
y = np.minimum(0, x)
print(len(y))
print_array(list(y))
