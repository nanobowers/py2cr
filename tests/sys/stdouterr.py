import sys

sys.stdout.write("Hello Stdout 1")
sys.__stdout__.write("Hello Stdout 2")

sys.stderr.write("Hello Stderr 1")
sys.__stderr__.write("Hello Stderr 2")

sys.stdout = sys.__stderr__
sys.stderr = sys.__stdout__
sys.stdout.write("Hello Stdout 3")
sys.stderr.write("Hello Stderr 3")

