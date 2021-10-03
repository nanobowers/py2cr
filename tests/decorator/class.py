

class foobar(object):
    
    x = 1

    def __init__(self):
        self.foovar = 1

    def foo(self,x):
        self.foovar = self.foovar + x

    def bar(self):
        print(self.foovar)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, data):
        self._x = data

    def set_x(self, x):
        self.x = x

f = foobar()
f.bar()
f.foo(1)
f.foo(2)
f.bar()
f.bar()
f.foo(-1)
f.bar()
f.foo(7)
f.bar()

f.x = 5
print(f.x)

f.set_x = 10
print(f.x)

