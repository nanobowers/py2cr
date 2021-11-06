# coding: utf-8
import numpy as np

def aryfmt(i):
    if float("%.3f" % abs(i)) == 0:
        return "%.3f" % abs(i)
    return "%.3f" % i
def print_array(data):
    print(" ".join(list([aryfmt(i) for i in data])))

""" Math functions """

x1 = np.arange(0, 6, 0.1, dtype=np.float64)

y1 = np.sqrt(x1)

for y in [x1]:
    print(len(y))
    print_array(list(y))
