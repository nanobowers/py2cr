import ast
import re
from typing import Any, Tuple
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
        "nan": "Float64::NAN",
        "NaN": "Float64::NAN",
        "inf": "Float64::INFINITY",
    }
    
    @staticmethod
    def parse_args(funcdb, type_from_args : bool) -> Tuple[Any, Any, Any]:
        templatetype = "Int32" # default value
        other_args = []
        other_raw_args = []
        for arg in funcdb.node.args:
            other_args.append(funcdb.crystal_visitor.visit(arg))
            other_raw_args.append(arg)
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
                other_args.append(funcdb.crystal_visitor.visit(kw))
                other_raw_args.append(kw)
        
        return (templatetype, other_args, other_raw_args)
    
    @staticmethod
    def _tensor(function, funcdb, type_from_args=False):
        templatetype, otherargs, _ = Numcr.parse_args(funcdb, type_from_args=type_from_args)
            
        arglist = ", ".join(otherargs)
        return f"Tensor({templatetype}, CPU({templatetype})).{function}({arglist})"

    @staticmethod
    def _tensor01(function, funcdb):
        """numpy.zeros/ones have a feature where first arg can be either array-like
        or a scalar. For num.cr we need to wrap it as an array in the scalar case""" 
        templatetype, _, other_raw_args = Numcr.parse_args(funcdb, type_from_args=False)
        argzero = funcdb.crystal_visitor.visit(other_raw_args[0])
        if isinstance(other_raw_args[0], ast.Constant):
            # First arg is a constant, convert to an Array
            arg0 = "[%s]" % argzero
        elif isinstance(other_raw_args[0], ast.Tuple):
            # first arg is a tuple, convert to Array
            arg0 = "%s.to_a" % argzero
        else:
            arg0 = argzero
        if len(other_raw_args) > 1:
            raise Exception("unexpected args for zeros/ones")
        return f"Tensor({templatetype}, CPU({templatetype})).{function}({arg0})"

    @staticmethod
    def num_class_method(funcdb, cls, method, first_to_tensor=True):
        # Some numpy methods accept a python array as a first-arg.
        # however for Num.cr, these methods require a Tensor, so we provide
        # a means to forcibly convert the firstarg to a tensor.
        if first_to_tensor:
            first = funcdb.crystal_args[0] + ".to_tensor"
            rest =  funcdb.crystal_args[1:]
            args = [first] + rest
            argstr = ", ".join(args)
            return "%s.%s(%s)" % (cls, method, argstr)
        else:
            argstr = ", ".join(funcdb.crystal_args)
            return "%s.%s(%s)" % (cls, method, argstr)


class NumpyRandom(CrystalTranslator):

    attribute_map = {}
    attribute_map.update(Numcr.typemap)
    
    def __init__(self):
        self.python_module_name = "numpy.random"
        # todo doesnt get picked up as np.random.* bc import resolution is half-baked.
        self.crystal_require = "num"
        
    def rand(funcdb):
        return Numcr._tensor("rand", funcdb)
    
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
        <Crystal> Tensor(Int32, CPU(Int32)).new([[0,1],[1,2])).to_a
        """
        args = funcdb.node.args
        firstarg = args[0]
        firstargstr = funcdb.crystal_visitor.visit(firstarg)
        return f"{firstargstr}.to_tensor"
        #if isinstance(firstarg, ast.Name):
        #    obj = funcdb.crystal_visitor.visit(firstarg)
        #else:
        #    obj = "firstarg.to_tensor" # Numcr._tensor('new', funcdb)
        #return f"{obj}.to_a"

    def shape(funcdb):
        ## inst method: np.shape(x) => x.shape
        firstarg = funcdb.node.args[0]
        inst = funcdb.crystal_visitor.visit(firstarg)
        return f"{inst}.shape"

    def copy(funcdb):
        ## inst method: np.copy(x) => x.dup
        firstarg = funcdb.node.args[0]
        inst = funcdb.crystal_visitor.visit(firstarg)
        return f"{inst}.dup"

    def array(funcdb):
        return Numcr._tensor("from_array", funcdb)

    def eye(funcdb):
        return Numcr._tensor("eye", funcdb)
    
    def identity(funcdb):
        return Numcr._tensor("identity", funcdb)

    def ones(funcdb):
        return Numcr._tensor01("ones", funcdb)

    def zeros(funcdb):
        return Numcr._tensor01("zeros", funcdb)
    
    def empty(funcdb):
        """ Same as zeros for Crystal per num.cr docs """
        return Numcr._tensor01("zeros", funcdb)

    def full(funcdb):
        return Numcr._tensor("full", funcdb)
    # LIKE FUNCTIONS
    
    def ones_like(funcdb):
        return Numcr._tensor("ones_like", funcdb)

    def zeros_like(funcdb):
        return Numcr._tensor("zeros_like", funcdb)

    def empty_like(funcdb):
        """ Same as zeros_like for Crystal per num.cr docs """
        return Numcr._tensor("zeros_like", funcdb)

    def full_like(funcdb):
        return Numcr._tensor("full_like", funcdb)


    # Space/range
    def linspace(funcdb):
        return Numcr._tensor("linear_space", funcdb)

    def geomspace(funcdb):
        return Numcr._tensor("geometric_space", funcdb)

    def logspace(funcdb):
        return Numcr._tensor("logarithmic_space", funcdb)

    def arange(funcdb):
        return Numcr._tensor("range", funcdb)

        
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
        return Numcr.num_class_method(funcdb, "Num", "all", first_to_tensor=True)
    def any(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "any", first_to_tensor=True)
    def sqrt(funcdb):
        return funcdb.wrap_class_method("Num", "sqrt")
    def sum(funcdb):
        return funcdb.wrap_class_method("Num", "sum")
    def asum(funcdb):
        return funcdb.wrap_class_method("Num", "asum")
    def prod(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "prod", first_to_tensor=True)

    def mean(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "mean", first_to_tensor=True)
    def max(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "max", first_to_tensor=True)
    def min(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "min", first_to_tensor=True)
    def amax(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "max", first_to_tensor=True)
    def amin(funcdb):
        return Numcr.num_class_method(funcdb, "Num", "min", first_to_tensor=True)
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
