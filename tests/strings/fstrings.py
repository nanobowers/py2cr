a = "dog\ndog\tdog"
b = 'cat'
c = '🐱'

print(f"001 {a}{b}{c}")
print(f'002 {a}{b}{c}')
print(f"""003 {a}{b}{c}""")

print(f"005 string {a!s} {b!s} {c!s}")
#broken print(f"006 ascii  {a!a} {b!a} {c!a}")

d = -177
print(f"int: {d}")

e = (1, 3, 5)

print(f'tuple: {e}')
print(f'tuple: {e!s}')
print(f'tuple: {e!r}')
#print(f'tuple: {e!a}')

