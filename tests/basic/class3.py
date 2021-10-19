class II(object):
    v = 1

class SS(object):
    v = "abcd"

class FF(object):
    v = 1.234

ii = II()
XX = II
xx = XX()
print(ii.v)
print(xx.v)
print(XX.v)


ss = SS()
YY = SS
yy = YY()
print(ss.v)
print(yy.v)
print(YY.v)


ff = FF()
ZZ = FF
zz = ZZ()
print(ff.v)
print(zz.v)
print(ZZ.v)

