import os
import sys

# sys.argv size
print(len(sys.argv))

# sys.argv[0] (program-name) will not be the same, so dont print it.
# print(sys.argv[0])

# first argument.
print(sys.argv[1])

# showing that argv can be modified
sys.argv[0] = "abcd"
sys.argv[1] = "abcd"

print(" ".join(sys.argv))
