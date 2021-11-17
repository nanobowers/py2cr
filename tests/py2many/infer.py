def foo():
    a = 10
    # infer that b is an int
    b = a
    assert b == 10
    print(b)


foo()
