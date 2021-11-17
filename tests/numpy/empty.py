# coding: utf-8
import numpy as np

def print_array(data):
    print(" ".join(list(["%.3f" % i for i in data])))

#x = np.empty(())
#print_array(x.shape)

x = np.empty((0))
print_array(x.shape)

x = np.empty((0,0))
print_array(x.shape)

x = np.empty(3, dtype=np.float32)
print_array(x.shape)

x = np.empty((2,3))
print_array(x.shape)

