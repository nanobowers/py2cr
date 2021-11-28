#import ast
from .translator import CrystalTranslator

class SixMoves(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "six.moves"
        self.crystal_require = None

    @staticmethod
    def range(funcdb) -> str:
        # six.moves.range() => range()
        comma_sep_args = ", ".join(funcdb.crystal_args)
        return f"PyRange.range({comma_sep_args})"

class Six(CrystalTranslator):
    attribute_map = {
        "PY2": "false",
        "PY3": "true",
        "integer_types": "[Int32]"
    }
    def __init__(self):
        super().__init__()
        self.python_module_name = "six"
        self.crystal_require = None

    @staticmethod
    def itervalues(funcdb) -> str:
        receiver = funcdb.crystal_args[0]
        return f"{receiver}.values"

    @staticmethod
    def iteritems(funcdb) -> str:
        receiver = funcdb.crystal_args[0]
        return f"{receiver}.to_a"
