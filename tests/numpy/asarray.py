import numpy as np

def print_array(data):
    print(" ".join(list(["%.3f" % i for i in data])))

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list(["%.3f" % i for i in d2])))
    print(']')


x = np.asarray([[1.,2.],[3.,4.]])
print_matrix(x)

x = np.asarray([1.,2.])
print_array(x)

y = np.asarray([3.,4.])
print_array(y)

z = (x + y)[0]
print(z)
