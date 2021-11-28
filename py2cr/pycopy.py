#import ast
from .translator import CrystalTranslator

class PythonCopy(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "copy"
        self.crystal_require = None

    @staticmethod
    def copy(funcdb) -> str:
        arg0 = funcdb.crystal_args[0]
        return f"{arg0}.dup"
