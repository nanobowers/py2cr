import ast
import re
from typing import Any, Tuple
from .translator import CrystalTranslator

def numcr__parse_args(funcdb) -> Tuple[Any, Any, Any]:
    """
    Many numpy methods take a keyword argument named `dtype`.
    For num.cr, we need to pull this dtype off of the list of
    keyword arguments and make convert it to a templated class.
    """
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

def numcr__tensor(function : str, funcdb) -> str:
    templatetype, otherargs, _ = numcr__parse_args(funcdb)

    arglist = ", ".join(otherargs)
    return f"Tensor({templatetype}, CPU({templatetype})).{function}({arglist})"

def numcr__tensor01(function : str, funcdb) -> str:
    """
    numpy.zeros/ones have a feature where first arg can be either array-like
    or a scalar. 
    For num.cr we need to wrap it as an array in the scalar case
    """
    templatetype, _, other_raw_args = numcr__parse_args(funcdb)
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

def numcr__class_method(funcdb, cls : str, method : str, first_to_tensor=True):
    # Some numpy methods accept a python array as a first-arg.
    # however for Num.cr, these methods require a Tensor, so we provide
    # a means to forcibly convert the firstarg to a tensor.
    if first_to_tensor:
        first = funcdb.crystal_args[0] + ".to_tensor"
        rest =  funcdb.crystal_args[1:]
        args = [first] + rest
        argstr = ", ".join(args)
    else:
        argstr = ", ".join(funcdb.crystal_args)
    return "%s.%s(%s)" % (cls, method, argstr)

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




class NumpyRandom(CrystalTranslator):

    attribute_map = {}
    attribute_map.update(Numcr.typemap)

    def __init__(self):
        super().__init__()
        self.python_module_name = "numpy.random"
        # TODO: doesnt get picked up as np.random.* bc import resolution is half-baked.
        self.crystal_require = "num"

    @staticmethod
    def rand(funcdb):
        return numcr__tensor("rand", funcdb)

class Numpy(CrystalTranslator):

    attribute_map = {}
    attribute_map.update(Numcr.typemap)

    def __init__(self):
        super().__init__()
        self.python_module_name = "numpy"
        self.crystal_require = "num"

    @staticmethod
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

    @staticmethod
    def shape(funcdb):
        ## inst method: np.shape(x) => x.shape
        firstarg = funcdb.node.args[0]
        inst = funcdb.crystal_visitor.visit(firstarg)
        return f"{inst}.shape"

    @staticmethod
    def copy(funcdb):
        ## inst method: np.copy(x) => x.dup
        firstarg = funcdb.node.args[0]
        inst = funcdb.crystal_visitor.visit(firstarg)
        return f"{inst}.dup"

    @staticmethod
    def array(funcdb):
        return numcr__tensor("from_array", funcdb)

    @staticmethod
    def eye(funcdb):
        return numcr__tensor("eye", funcdb)

    @staticmethod
    def identity(funcdb):
        return numcr__tensor("identity", funcdb)

    @staticmethod
    def ones(funcdb):
        return numcr__tensor01("ones", funcdb)

    @staticmethod
    def zeros(funcdb):
        return numcr__tensor01("zeros", funcdb)

    @staticmethod
    def empty(funcdb):
        """ Same as zeros for Crystal per num.cr docs """
        return numcr__tensor01("zeros", funcdb)

    @staticmethod
    def full(funcdb):
        return numcr__tensor("full", funcdb)

    # LIKE FUNCTIONS

    @staticmethod
    def ones_like(funcdb):
        return numcr__tensor("ones_like", funcdb)

    @staticmethod
    def zeros_like(funcdb):
        return numcr__tensor("zeros_like", funcdb)

    @staticmethod
    def empty_like(funcdb):
        """ Same as zeros_like for Crystal per num.cr docs """
        return numcr__tensor("zeros_like", funcdb)

    @staticmethod
    def full_like(funcdb):
        return numcr__tensor("full_like", funcdb)


    # Space/range
    @staticmethod
    def linspace(funcdb):
        return numcr__tensor("linear_space", funcdb)

    @staticmethod
    def geomspace(funcdb):
        return numcr__tensor("geometric_space", funcdb)

    @staticmethod
    def logspace(funcdb):
        return numcr__tensor("logarithmic_space", funcdb)

    @staticmethod
    def arange(funcdb):
        return numcr__tensor("range", funcdb)


    # TRIG FUNCTIONS
    @staticmethod
    def cos(funcdb):
        return funcdb.wrap_class_method("Num", "cos")
    @staticmethod
    def sin(funcdb):
        return funcdb.wrap_class_method("Num", "sin")
    @staticmethod
    def tan(funcdb):
        return funcdb.wrap_class_method("Num", "tan")
    @staticmethod
    def arccos(funcdb):
        return funcdb.wrap_class_method("Num", "acos")
    @staticmethod
    def arcsin(funcdb):
        return funcdb.wrap_class_method("Num", "asin")
    @staticmethod
    def arctan(funcdb):
        return funcdb.wrap_class_method("Num", "atan")

    @staticmethod
    def cosh(funcdb):
        return funcdb.wrap_class_method("Num", "cosh")
    @staticmethod
    def sinh(funcdb):
        return funcdb.wrap_class_method("Num", "sinh")
    @staticmethod
    def tanh(funcdb):
        return funcdb.wrap_class_method("Num", "tanh")
    @staticmethod
    def arccosh(funcdb):
        return funcdb.wrap_class_method("Num", "acosh")
    @staticmethod
    def arcsinh(funcdb):
        return funcdb.wrap_class_method("Num", "asinh")
    @staticmethod
    def arctanh(funcdb):
        return funcdb.wrap_class_method("Num", "atanh")
    ## non-trig
    @staticmethod
    def all(funcdb):
        return numcr__class_method(funcdb, "Num", "all", first_to_tensor=True)
    @staticmethod
    def any(funcdb):
        return numcr__class_method(funcdb, "Num", "any", first_to_tensor=True)
    @staticmethod
    def sqrt(funcdb):
        return funcdb.wrap_class_method("Num", "sqrt")
    @staticmethod
    def sum(funcdb):
        return funcdb.wrap_class_method("Num", "sum")
    @staticmethod
    def asum(funcdb):
        return funcdb.wrap_class_method("Num", "asum")
    @staticmethod
    def prod(funcdb):
        return numcr__class_method(funcdb, "Num", "prod", first_to_tensor=True)

    @staticmethod
    def mean(funcdb):
        return numcr__class_method(funcdb, "Num", "mean", first_to_tensor=True)
    @staticmethod
    def max(funcdb):
        return numcr__class_method(funcdb, "Num", "max", first_to_tensor=True)
    @staticmethod
    def min(funcdb):
        return numcr__class_method(funcdb, "Num", "min", first_to_tensor=True)
    @staticmethod
    def amax(funcdb):
        return numcr__class_method(funcdb, "Num", "max", first_to_tensor=True)
    @staticmethod
    def amin(funcdb):
        return numcr__class_method(funcdb, "Num", "min", first_to_tensor=True)
    @staticmethod
    def argmax(funcdb):
        return funcdb.wrap_class_method("Num", "argmax")
    @staticmethod
    def argmin(funcdb):
        return funcdb.wrap_class_method("Num", "argmin")

class Collections(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "collections"
        self.crystal_require = None

    @staticmethod
    def OrderedDict(funcdb):
        # replace with first arg (a dict)
        return funcdb.crystal_args[0]
