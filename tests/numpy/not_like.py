# coding: utf-8
import numpy as np

def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(int("%d" % j))
        data_i.append(data_j)
    print(data_i)

def print_array(data):
    datas = []
    for i in data:
        if float("%.3f" % abs(i)) == 0:
            datas.append(float("%.3f" % abs(i)))
        else:
            datas.append(float("%.3f" % i))
    print(datas)

x1 = np.ones(5, dtype=np.int8)
print_array(x1)

x2 = np.ones(5)
print_array(x2)

x3 = np.zeros(5)
print_array(x3)

x4 = np.full((2, 2), 1)
print_matrix(x4)

#x = np.empty([2, 2])
#print(list(x.shape))


