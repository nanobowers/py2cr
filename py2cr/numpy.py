import ast
import re
from .translator import *

class Numcr:
    typemap = {
        "int8": "Int8",
        "int16": "Int8",
        "int32": "Int32",
        "int64": "Int64",
        "int":   "Int64",
        "uint8": "UInt8",
        "uint16": "UInt8",
        "uint32": "UInt32",
        "uint64": "UInt64",
        "uint":   "UInt64",
        "float32": "Float32",
        "float64": "Float64",
    }
    
    @staticmethod
    def parse_args(funcdb):
        templatetype = "Int32" # default value
        otherargs = []
        for arg in funcdb.node.args:
            otherargs.append(funcdb.crystal_visitor.visit(arg))
            
        for kw in funcdb.node.keywords:
            if kw.arg == "dtype":
                dtype_value = funcdb.crystal_visitor.visit(kw.value)
                # remove preceding np./numpy. to get dtype for lookup
                dtype_value_hack = re.sub(r".*\.", '', dtype_value)
                templatetype = Numcr.typemap[dtype_value_hack]
            else:
                otherargs.append(funcdb.crystal_visitor.visit(kw))
        
        return (templatetype, otherargs)
    
    @staticmethod
    def _tensor(function, funcdb):
        templatetype, otherargs = Numcr.parse_args(funcdb)
            
        arglist = ", ".join(otherargs)
        return f"Tensor({templatetype}).{function}({arglist})"

class Numpy(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "numpy"
        self.crystal_require = "num"

    def arange(funcdb):
        return Numcr._tensor("range", funcdb)
    
    def ones(funcdb):
        return Numcr._tensor("ones", funcdb)

    def zeros(funcdb):
        return Numcr._tensor("zeros", funcdb)

    def ones_like(funcdb):
        return Numcr._tensor("ones_like", funcdb)

    def zeros_like(funcdb):
        return Numcr._tensor("zeros_like", funcdb)

    
class Collections(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "collections"
        self.crystal_require = None

    def OrderedDict(funcdb):
        # replace with first arg (a dict)
        return funcdb.crystal_args[0]
