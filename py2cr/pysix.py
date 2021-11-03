import ast
from .translator import *
    
class SixMoves(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "six.moves"
        self.crystal_require = None

    def range(funcdb):
        # six.moves.range() => range()
        return "PyRange.range(%s)" % ", ".join(funcdb.crystal_args)
    
class Six(CrystalTranslator):
    attribute_map = {
        "PY2": "false",
        "PY3": "true",
        "integer_types": "[Int32]"
    }
    def __init__(self):
        self.python_module_name = "six"
        self.crystal_require = None

    def itervalues(funcdb):
        receiver = funcdb.crystal_args[0]
        return f"{receiver}.values"
    
    def iteritems(funcdb):
        receiver = funcdb.crystal_args[0]
        return f"{receiver}.to_a"
