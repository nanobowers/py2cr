x = None
y = False
z = True
a = 1

if x == None:
    print("x is None/nil")
else:
    print("illegal")

if x is None:
    print("x is None/nil")
else:
    print("illegal")

if x is not None:
    print("illegal (x is not None)")
else:
    print("x is not None/nil")
    
if y is not None:
    print("y is not None/nil")
else:
    print("illegal (y is not None)")

    
if z != None:
    print("z is not None/nil")
else:
    print("illegal")

if not a is None:
    print("a is not None/nil")
else:
    print("illegal")

if not a == None:
    print("a is not None/nil")
else:
    print("illegal")
