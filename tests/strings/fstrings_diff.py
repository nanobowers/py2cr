# these print differently in python and crystal

a = "dog\ndog\tdog"
b = 'cat'
c = '🐱'
print(f"004 repr   {a!r} {b!r} {c!r}")

c = 1.234E-6
print(f"float: {c}")

f = ["b", 'c', 'd', 7]

print(f'list: {f}')
print(f'list: {f!s}')
print(f'list: {f!r}')
#print(f'list: {f!a}')

