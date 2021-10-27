import ast
from .translator import *

class PySys(CrystalTranslator):
    attribute_map = {
        "__stdin__": "PySys.__stdin__",
        "__stdout__": "PySys.__stdout__",
        "__stderr__": "PySys.__stderr__",
        "stdin": "PySys.stdin",
        "stdout": "PySys.stdout",
        "stderr": "PySys.stderr",
        "argv": "PySys.argv",
    }
    def __init__(self):
        self.python_module_name = "sys"
        self.crystal_require = None

    def exit(funcdb):
        return "exit(%s)" % ", ".join(funcdb.crystal_args)
