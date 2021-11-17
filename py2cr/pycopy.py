import ast
from .translator import *

class PythonCopy(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "copy"
        self.crystal_require = None

    def copy(funcdb):
        return "%s.dup" % (funcdb.crystal_args[0])
