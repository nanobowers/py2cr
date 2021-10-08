try:
    raise
except:
    pass

try:
    raise NotImplementedError('User Defined Error Message.')
except NotImplementedError as err:
    print('NotImplementedError')
except:
    print('Error :')

try:
    raise KeyError('missing key')
except KeyError as ex:
    print('KeyError')
except:
    print('Error :')

try:
    1 // 0
except ZeroDivisionError as ex:
    print('ZeroDivisionError')
except:
    print('Error :')

try:
    raise RuntimeError("runtime!")
except RuntimeError as ex:
    print('RuntimeError :', ex)
except:
    print('Error :')
