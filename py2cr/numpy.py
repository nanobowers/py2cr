import ast
from .translator import *

class Numpy(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "numpy"
        self.crystal_require = "num"
        
    def arange(self):
        return "ARANGE"
    
class Collections(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "collections"
        self.crystal_require = None

    def OrderedDict(funcdb):
        # replace with first arg (a dict)
        return funcdb.crystal_args[0]
    
class SixMoves(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "six.moves"
        self.crystal_require = None

    def range(funcdb):
        # six.moves.range() => range()
        return PythonMain.range(funcdb)
    
