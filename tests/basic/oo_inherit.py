from typing import List

class bar(object):

    def __init__(self,name : str):
        self.name = name

    def setname(self,name):
        self.name = name

class foo(bar):
    
    registered : List["foo"] = []

    def __init__(self, val : int, name : str):
        self.fval = val
        self.register(self)
        bar.__init__(self, name)

    def inc(self):
        self.fval += 1

    def msg(self,*varargs):
        txt = ''
        for arg in varargs:
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
