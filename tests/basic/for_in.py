from typing import List, Dict

# iterating over a list
print('-- list --')
a = [1,2,3,4,5]
for x in a:
    print(x)

# iterating over a tuple
print('-- tuple else case --')
t = ('cats','dogs','squirrels')
for x1 in t:
    print(x1)
else:
    print('ok')

print('-- tuple else break case --')
for x2 in t:
    print(x2)
    if x2 == 'squirrels':
        break
else:
    print('ok')

# iterating over a dictionary
# sort order in python is undefined, so need to sort the results
# explictly before comparing output

print('-- dict keys --')
dct = {'a':1,'b':2,'c':3 }

keys : List[str] = []
for x3 in dct.keys():
    keys.append(x3)

keys.sort()
for k in keys:
    print(k)

print('-- dict values --')
values : List[int] = list()
for v in dct.values():
    values.append(v)

values.sort()
for v in values:
    print(v)

items : Dict[str,int] = dict()
for k, v in dct.items():
    items[k] = v

print('-- dict item --')
print(items['a'])
print(items['b'])
print(items['c'])

# iterating over a string
print('-- string --')
aaa = 'defabc'
for x4 in aaa:
    print(x4)

