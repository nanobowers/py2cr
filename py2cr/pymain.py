import ast
import sys
from .translator import CrystalTranslator
from .errors import CrystalError

class PythonTyping(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "typing"
        self.crystal_require = None

class PythonFunctools(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "functools"
        self.crystal_require = None

class PythonRand(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "random"
        self.crystal_require = None

    @staticmethod
    def random(funcdb):
        return funcdb.wrap_class_method("Random", "rand")

class PythonMain(CrystalTranslator):
    """For functions/attributes not in a module"""
    def __init__(self):
        super().__init__()
        self.python_module_name = ""
        self.crystal_require = None

    @staticmethod
    def int(funcdb) -> str:
        """
        <Py2cr.0> int() => 0
        <Py2cr.1> int(val) => val.to_i
        <Py2cr.2> int(astr,basenum) => astr.to_i(basenum)
        """
        cvisit = funcdb.crystal_visitor
        filt_args = [cvisit.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return "0"
        elif func_args == 1:
            return f"{filt_args[0]}.to_i"
        elif func_args == 2:
            return "%s.to_i(%s)" % (filt_args[0], filt_args[1])
        raise ValueError("Expecting 0..2 args")

    @staticmethod
    def float(funcdb) -> str:
        """
        <Py2cr.0> float() => 0
        <Py2cr.1> float(val) => val.to_f
        <Py2cr.2> float(astr,basenum) => astr.to_f(basenum)
        """
        cvisit = funcdb.crystal_visitor
        filt_args = [cvisit.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return "0.0"
        elif func_args == 1:
            return "%s.to_f" % (filt_args[0])
        raise ValueError("Expecting 0..1 args")

    @staticmethod
    def str(funcdb) -> str:
        # <Py2cr.0> str() => ""
        # <Py2cr.1> str(val) => val.to_s
        # <Py2cr.2> str(astr,basenum) => astr.to_i(basenum)
        cvisit = funcdb.crystal_visitor
        filt_args = [cvisit.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return '""'
        elif func_args == 1:
            arg0 = filt_args[0]
            return f"{arg0}.to_s"
        # all else fails warn and do something
        sys.stderr.write("Cannot handle str() with more than one arg.\n")
        comma_sep_args = ','.join(filt_args)
        return f"str({comma_sep_args})"


    @staticmethod
    def range(funcdb) -> str:
        # range one-arg
        #  <Python>    range(3) ==> [0,1,2]
        #  <Crystal>   3.times
        # two args (start, stop)
        #  <Python>    range(2,5) ==> [2, 3, 4]
        #  <Crystal>   PyLib.range(2, 5)
        # three args (start, stop, step)
        #  <Python>    range(1,10,3) ==>  [1, 4, 7]
        #  <Crystal>   PyLib.range(1, 10, 3)
        cvisit = funcdb.crystal_visitor
        node = funcdb.node
        filt_args = [cvisit.ope_filter(x) for x in funcdb.crystal_args]

        if len(node.args) == 1:
            start = filt_args[0]
            return f"{start}.times"
        elif len(node.args) == 2:
            start, stop = filt_args[0:]
            return f"PyRange.range({start}, {stop})"
        else:
            start, stop, step = filt_args[0:]
            return f"PyRange.range({start}, {stop}, {step})"

    @staticmethod
    def reduce(funcdb) -> str:
        cvisit = funcdb.crystal_visitor
        cry_args = funcdb.crystal_args
        node = funcdb.node
        func = funcdb.funcstr

        # Reduce gets either a lambda or a block
        if isinstance(node.args[0], ast.Lambda):
            # reduce(lambda x: x**2, alist)
            block = cvisit.visit_Lambda(node.args[0], style="block")
        else:
            # reduce(foo, alist)
            block = "{ |*args| %s(*args) }" % cry_args[0]

        if len(cry_args) > 2:
            # <Python>   reduce(foo, alist, 10)
            # <Crystal>  alist.reduce(10) { |*args| foo(*args) }
            return "%s.%s(%s) %s" % (cry_args[1], func, cry_args[2], block)
        else:
            # <Python>   reduce(foo, alist)
            # <Crystal>  alist.reduce { |*args| foo(*args) }
            return "%s.%s %s" % (cry_args[1], func, block)


    @staticmethod
    def map(funcdb) -> str:
        # map - lambda Call
        # <Python>    map(lambda x: x**2, [1,2])
        # <Crystal>   [1, 2].map{|x| x**2}
        # map - block
        # <Python>    map(foo, [1, 2])
        # <Crystal>   [1, 2].map{|_| foo(_) }
        cvisit = funcdb.crystal_visitor
        cry_args = funcdb.crystal_args
        node = funcdb.node
        func = funcdb.funcstr
        if isinstance(node.args[0], ast.Lambda):
            block = cvisit.visit_Lambda(node.args[0], style="block")
            return "%s.%s %s" % (cry_args[1], func, block)
        else:
            return "%s.%s {|v| %s(v)}" % (cry_args[1], func, cry_args[0])

    @staticmethod
    def tuple(funcdb) -> str:
        # <Python>    tuple(range(3))
        # <Crystal>   3.times.to_a
        cry_args_s = ' '.join(funcdb.crystal_args)
        if len(funcdb.node.args) == 0:
            return "Tuple.new()"
        elif (len(funcdb.node.args) == 1) and isinstance(funcdb.node.args[0], ast.Str):
            return f"{cry_args_s}.split(\"\")"
        else:
            return f"{cry_args_s}.to_a"

    @staticmethod
    def list(funcdb) -> str:
        # <Python>    list(range(3))
        # <Crystal>   3.times.to_a
        cry_args_s = ' '.join(funcdb.crystal_args)
        if len(funcdb.node.args) == 0:
            return funcdb.empty_list()
        elif (len(funcdb.node.args) == 1) and isinstance(funcdb.node.args[0], ast.Str):
            return f"{cry_args_s}.split(\"\")"
        else:
            return f"{cry_args_s}.to_a"

    @staticmethod
    def dict(funcdb) -> str:
        # <Python>    dict([('foo', 1), ('bar', 2)])
        # <Crystal>   {'foo' => 1, 'bar' => 2}
        cvisit = funcdb.crystal_visitor
        if len(funcdb.node.args) == 0:
            return funcdb.empty_hash()
        elif len(funcdb.node.args) == 1:
            if isinstance(funcdb.node.args[0], ast.List):
                cry_args = []
                for elt in funcdb.node.args[0].elts:
                    cvisit._tuple_type = '=>'
                    cry_args.append(cvisit.visit(elt))
                    cvisit._tuple_type = '[]'
            elif isinstance(funcdb.node.args[0], ast.Dict):
                return cvisit.visit(funcdb.node.args[0])
            elif isinstance(funcdb.node.args[0], ast.Name):
                return cvisit.visit(funcdb.node.args[0]) + ".dup"
        else:
            cvisit.set_result(2)
            raise CrystalError("dict in argument list Error")
        return "{" + ", ".join(cry_args) + "}"
