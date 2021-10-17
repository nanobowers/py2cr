def abs(x):
    if x > 0:
        return x
    else:
        return -x

def sqrt(x):
    eps = 1e-10
    x = float(x)
    r = x/2
    residual = r**2 - x
    while abs(residual) > eps:
        r_d = -residual/(2*r)
        r += r_d
        residual = r**2 - x
    return r

def p(x):
    return "%.10f" % x

print((p(sqrt(1))))
print((p(sqrt(2))))
print((p(sqrt(3))))
print((p(sqrt(4))))
print((p(sqrt(5))))
print((p(sqrt(6))))
print((p(sqrt(7000))))
