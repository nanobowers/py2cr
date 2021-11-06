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
        # self-mapping in case prop was already mapped somehow
        "Int8": "Int8",
        "Int16": "Int8",
        "Int32": "Int32",
        "Int64": "Int64",
        "UInt8": "UInt8",
        "UInt16": "UInt8",
        "UInt32": "UInt32",
        "UInt64": "UInt64",
        "Float32": "Float32",
        "Float64": "Float64",
        # ndarray map to Tensor
        "ndarray": "Tensor",
    }
    
    @staticmethod
    def parse_args(funcdb):
        templatetype = "Int32" # default value
        otherargs = []
        for arg in funcdb.node.args:
            otherargs.append(funcdb.crystal_visitor.visit(arg))
            
        for kw in funcdb.node.keywords:
            if kw.arg == "dtype":
                if isinstance(kw.value, ast.Str):
                    dtype_value = kw.value.s # unquoted str-value
                else:
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

    attribute_map = {}
    attribute_map.update(Numcr.typemap)
    
    def __init__(self):
        self.python_module_name = "numpy"
        self.crystal_require = "num"

    def asarray(funcdb):
        """
        <Python> np.asarray(x)
        <Crystal> x.to_a

        <Python> np.asarray([[0,1],[1,2]])
        <Crystal> Tensor(Int32).new([[0,1],[1,2])).to_a
        """
        args = funcdb.node.args
        firstarg = args[0]
        if isinstance(firstarg, ast.Name):
            obj = funcdb.crystal_visitor.visit(firstarg)
        else:
            obj = Numcr._tensor('new', funcdb)
        return f"{obj}.to_a"

    def arange(funcdb):
        return Numcr._tensor("range", funcdb)

    def array(funcdb):
        return Numcr._tensor("from_array", funcdb)
    
    def ones(funcdb):
        return Numcr._tensor("ones", funcdb)

    def zeros(funcdb):
        return Numcr._tensor("zeros", funcdb)

    def ones_like(funcdb):
        return Numcr._tensor("ones_like", funcdb)

    def zeros_like(funcdb):
        return Numcr._tensor("zeros_like", funcdb)

    def linspace(funcdb):
        return Numcr._tensor("linear_space", funcdb)

    # TRIG FUNCTIONS
    def cos(funcdb):
        return funcdb.wrap_class_method("Num", "cos")
    def sin(funcdb):
        return funcdb.wrap_class_method("Num", "sin")
    def tan(funcdb):
        return funcdb.wrap_class_method("Num", "tan")
    def arccos(funcdb):
        return funcdb.wrap_class_method("Num", "acos")
    def arcsin(funcdb):
        return funcdb.wrap_class_method("Num", "asin")
    def arctan(funcdb):
        return funcdb.wrap_class_method("Num", "atan")

    def cosh(funcdb):
        return funcdb.wrap_class_method("Num", "cosh")
    def sinh(funcdb):
        return funcdb.wrap_class_method("Num", "sinh")
    def tanh(funcdb):
        return funcdb.wrap_class_method("Num", "tanh")
    def arccosh(funcdb):
        return funcdb.wrap_class_method("Num", "acosh")
    def arcsinh(funcdb):
        return funcdb.wrap_class_method("Num", "asinh")
    def arctanh(funcdb):
        return funcdb.wrap_class_method("Num", "atanh")
    ## non-trig
    def all(funcdb):
        return funcdb.wrap_class_method("Num", "all")
    def any(funcdb):
        return funcdb.wrap_class_method("Num", "any")
    def argmax(funcdb):
        return funcdb.wrap_class_method("Num", "argmax")
    def argmin(funcdb):
        return funcdb.wrap_class_method("Num", "argmin")
    def sqrt(funcdb):
        return funcdb.wrap_class_method("Num", "sqrt")
    def sum(funcdb):
        return funcdb.wrap_class_method("Num", "sum")
    def asum(funcdb):
        return funcdb.wrap_class_method("Num", "asum")
    def prod(funcdb):
        return funcdb.wrap_class_method("Num", "prod")

    def max(funcdb):
        return funcdb.wrap_class_method("Num", "max")
    def min(funcdb):
        return funcdb.wrap_class_method("Num", "min")
    def amax(funcdb):
        return funcdb.wrap_class_method("Num", "amax")
    def amin(funcdb):
        return funcdb.wrap_class_method("Num", "amin")
    def argmax(funcdb):
        return funcdb.wrap_class_method("Num", "argmax")
    def argmin(funcdb):
        return funcdb.wrap_class_method("Num", "argmin")
    
class Collections(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "collections"
        self.crystal_require = None

    def OrderedDict(funcdb):
        # replace with first arg (a dict)
        return funcdb.crystal_args[0]
