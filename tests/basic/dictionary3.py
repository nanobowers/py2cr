from typing import Dict

foo : Dict[str,str] = dict()
foo['a'] = 'b'
foo['c'] = 'd'

print(foo['a'])
print(foo['c'])

bar = dict([('a', 1), ('b', 2), ('c', 3)])
if 'a' in bar:
    print("a in bar")
