import os

randomkey = "f0f18c4e0b04edaef0126c9720fd"

if randomkey not in os.environ:
    print("Intentionally missing random unknown env-var")

os.environ[randomkey] = "999"

print(os.environ[randomkey])

print(os.environ["PATH"])

