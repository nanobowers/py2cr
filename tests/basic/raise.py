

a = [1, 2]

try:
    try:
        print("Trying illegal access")
        z = a[5]
    except:
        print("Exception raised, re-raising")
        raise
except:
    print("Exception raised")
    pass
