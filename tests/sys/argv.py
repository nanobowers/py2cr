import os
import sys

# sys.argv size
print(len(sys.argv))

# program-name, minus .## extension (.py or .rb)
print(sys.argv[0][0:-3])

# first argument.
print(sys.argv[1])

# showing that argv can be modified
sys.argv[0] = "abcd"
sys.argv[1] = "abcd"

print(" ".join(sys.argv))
