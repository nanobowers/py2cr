import os
import sys

# sys.argv size
print(len(sys.argv))

# sys.argv[0] (program-name) will not be the same, so dont print it.
# print(sys.argv[0])

# first argument.  should raise IndexError if no arg given
try:
    print(sys.argv[1])
except IndexError:
    print("Missing sys.argv[1]")

