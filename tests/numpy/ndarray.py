import numpy as np

a = np.array([1,2,3,4,5], dtype='int32')
if isinstance(a, np.ndarray):
    print('OK')
else:
    print('NG')

