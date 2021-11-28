#import ast
from .translator import CrystalTranslator

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
        super().__init__()
        self.python_module_name = "sys"
        self.crystal_require = None

    @staticmethod
    def exit(funcdb) -> str:
        comma_sep_args = ", ".join(funcdb.crystal_args)
        return f"exit({comma_sep_args})"
