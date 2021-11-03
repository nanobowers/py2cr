import numpy as np

def print_array(data):
    print(" ".join(list(["%d" % i for i in data])))

x = np.array([1, 2, 3])
print_array(x)
y = np.copy(x)
print_array(y)
x[0] = 10
print_array(x)
print_array(y)

