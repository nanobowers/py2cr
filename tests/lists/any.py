from typing import List, Dict, Tuple

empty_list : List[int] = []
empty_dict : Dict[str,int] = {}
empty_tuple = ()

l = [4,7,3,4,2,1]
v = any(l)
print(str(v).upper())

print(str(any(empty_list)).upper())
print(str(any(empty_dict)).upper())
print(str(any(empty_tuple)).upper())
print(str(any([False])).upper())
print(str(any([None])).upper())
print(str(any([0])).upper())
print(str(any([''])).upper())
print(str(any([empty_list])).upper())
print(str(any([empty_dict])).upper())

l = [0,empty_dict]
v = any(l)
print(str(v).upper())
