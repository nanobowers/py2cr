
class bar(object):

    def __init__(self,name):
        self.name = name

    def setname(self,name):
        self.name = name

class foo(bar):
    
    registered = []

    def __init__(self,val,name):
        self.fval = val
        self.register(self)
        self.name = name

    def inc(self):
        self.fval += 1

    def msg(self, a=None, b=None, c=None):
        txt = ''
        varargs = a, b, c
        for arg in varargs:
            if arg is None:
                continue
            txt += str(arg)
            txt += ","
        return txt + self.name + " says:"+str(self.fval)

    @staticmethod
    def register(f):
        foo.registered.append(f)

    @staticmethod
    def printregistered():
        for r in foo.registered:
            print(r.msg())

a = foo(10,'a')
a.setname('aaa')
b = foo(20,'b')
c = foo(30,'c')

a.inc()
a.inc()
c.inc()

print(a.msg())
print(b.msg())
print(c.msg(2,3,4))

print("---")

foo.printregistered()
