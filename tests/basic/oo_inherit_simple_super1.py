from typing import List

class Bar(object):

    def __init__(self,name : str):
        self.name = name

    def setname(self,name):
        self.name = name

class Foo(Bar):
    
    registered : List[int] = []

    def __init__(self,val : int ,name : str):
        self.fval = val
        self.register(self)
        Bar.__init__(self,name)

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
        Foo.registered.append(f)

    @staticmethod
    def printregistered():
        for r in Foo.registered:
            print(r.msg())

a = Foo(10,'a')
a.setname('aaa')
b = Foo(20,'b')
c = Foo(30,'c')

a.inc()
a.inc()
c.inc()

print(a.msg())
print(b.msg())
print(c.msg(2,3,4))

print("---")

Foo.printregistered()
