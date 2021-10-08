from typing import List, Dict, Tuple

empty_list : List[int] = []
empty_dict : Dict[str,int] = {}
empty_tuple = ()

l = [4,7,3,4,2,1]
v = all(l)
print(str(v).upper())

print(str(all(empty_list)).upper())
print(str(all(empty_dict)).upper())
print(str(all(empty_tuple)).upper())
print(str(all([False])).upper())
print(str(all([None])).upper())
print(str(all([0])).upper())
print(str(all([''])).upper())
print(str(all([empty_list])).upper())
print(str(all([empty_dict])).upper())

l = [0,empty_dict]
v = all(l)
print(str(v).upper())
