from typing import Set

# iterating over a list
print('-- set --')
a : Set[int] = set([1,2,3,4,5])
a.remove(3)
for x in a:
    print(x)

print('-- set add --')
b : Set[int] = set()
b.add(1)
b.add(2)
b.add(1)
for x in b:
    print(x)

print('-- set clear --')

b.clear() 
for x in b:
    print(x)
