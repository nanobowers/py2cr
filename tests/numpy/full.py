# coding: utf-8
import numpy as np

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

x = np.full((2, 2), 5, dtype=np.int64)
print_matrix(x)

