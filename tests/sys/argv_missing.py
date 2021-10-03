import os
import sys

# sys.argv size
print(len(sys.argv))

# program-name, minus .## extension
print(sys.argv[0][0:-3])

# first argument.  should raise IndexError if no arg given
try:
    print(sys.argv[1])
except IndexError:
    print("Missing sys.argv[1]")

