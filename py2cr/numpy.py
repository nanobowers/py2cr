from .translator import *

class Numpy(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "numpy"
        self.crystal_require = "num"
        
    def arange(self):
        pass
    

class Os(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "os"
        self.crystal_require = None
        
    def walk(self):
        pass
    
