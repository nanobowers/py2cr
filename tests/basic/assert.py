# should not assert
try:
    assert True, "no message"
except AssertionError as err:
    print('AssertionError :', err)
except:
    print('Error :')

# assert with a message
try:
    assert False, "error message"
except AssertionError as err:
    print('AssertionError :', err)
except:
    print('Error :')

# assert with no message
try:
    assert False
except AssertionError as err:
    print('AssertionError with no message')
except:
    print('Other Error')
