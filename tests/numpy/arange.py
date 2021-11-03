import numpy as np

def aryfmt(i):
    if float("%.3f" % abs(i)) == 0:
        return "%.3f" % abs(i)
    return "%.3f" % i
def print_array(data):
    print(" ".join(list([aryfmt(i) for i in data])))

x = np.arange(-1.0, 1.0, 0.1, dtype=np.float64)
print_array(x)
x = np.arange(6)
print_array(x)
x = np.arange(1,6) 
print_array(x)
x = np.arange(1,6,2)
print_array(x)

