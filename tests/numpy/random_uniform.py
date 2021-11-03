import numpy as np

def print_matrix(data):
    print('[')
    for d2 in list(data):
        print("  " + ", ".join(list([str(int(i)) for i in d2])))
    print(']')

x = np.random.uniform(-1, 1, (3,2))

y = np.array(x < 1, dtype=np.int)
print_matrix(y)

y = np.array(x > -1, dtype=np.int)
print_matrix(y)

x = np.random.uniform(-1, 1)
x = np.asarray(x)
print(x.ndim)

