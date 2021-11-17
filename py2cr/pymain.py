import ast
from .translator import *

class PythonTyping(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "typing"
        self.crystal_require = None

class PythonFunctools(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "functools"
        self.crystal_require = None

class PythonRand(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "random"
        self.crystal_require = None

    def random(funcdb):
        return funcdb.wrap_class_method("Random", "rand")
    
class PythonMain(CrystalTranslator):
    """For functions/attributes not in a module"""
    def __init__(self):
        self.python_module_name = ""
        self.crystal_require = None

    def int(funcdb):
        """
        <Py2cr.0> int() => 0
        <Py2cr.1> int(val) => val.to_i
        <Py2cr.2> int(astr,basenum) => astr.to_i(basenum)
        """
        cv = funcdb.crystal_visitor
        filt_args = [cv.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return "0"
        elif func_args == 1:
            return "%s.to_i" % (filt_args[0])
        elif func_args == 2:
            return "%s.to_i(%s)" % (filt_args[0:2])
        raise ArgumentError("Expecting 0..2 args")
    
    def float(funcdb):
        """
        <Py2cr.0> float() => 0
        <Py2cr.1> float(val) => val.to_f
        <Py2cr.2> float(astr,basenum) => astr.to_f(basenum)
        """
        cv = funcdb.crystal_visitor
        filt_args = [cv.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return "0.0"
        elif func_args == 1:
            return "%s.to_f" % (filt_args[0])
        raise ArgumentError("Expecting 0..1 args")
    
    def str(funcdb):
        """
        <Py2cr.0> str() => ""
        <Py2cr.1> str(val) => val.to_s
        <Py2cr.2> str(astr,basenum) => astr.to_i(basenum)
        """
        cv = funcdb.crystal_visitor
        filt_args = [cv.ope_filter(x) for x in funcdb.crystal_args]
        func_args = len(funcdb.node.args)
        if func_args == 0:
            return '""'
        elif func_args == 1:
            return "%s.to_s" % (filt_args[0])
        # all else fails warn and do something
        sys.stderr.write("Cannot handle str() with more than one arg.\n")
        return "%s(%s)" % (func, ",".join(filt_args))

    
    def range(funcdb):
        """ 
        # range one-arg
        <Python>    range(3) ==> [0,1,2]
        <Crystal>   3.times 
        # two args (start, stop)
        <Python>    range(2,5) ==> [2, 3, 4] 
        <Crystal>   PyLib.range(2, 5)
        # three args (start, stop, step)
        <Python>    range(1,10,3) ==>  [1, 4, 7] 
        <Crystal>   PyLib.range(1, 10, 3) 
        """
        cv = funcdb.crystal_visitor
        node = funcdb.node
        filt_args = [cv.ope_filter(x) for x in funcdb.crystal_args]
        
        if len(node.args) == 1:
            return "%s.times" % (filt_args[0])
        elif len(node.args) == 2:
            start, stop = filt_args[0:]
            return f"PyRange.range({start}, {stop})"
        else:
            start, stop, step = filt_args[0:]
            return f"PyRange.range({start}, {stop}, {step})"

    def reduce(funcdb):
        cv = funcdb.crystal_visitor
        cry_args = funcdb.crystal_args
        node = funcdb.node
        func = funcdb.funcstr

        # Reduce gets either a lambda or a block
        if isinstance(node.args[0], ast.Lambda):
            """ reduce(lambda x: x**2, alist) """
            block = cv.visit_Lambda(node.args[0], style="block")
        else:
            """ reduce(foo, alist) """
            block = "{ |*args| %s(*args) }" % cry_args[0]

        if len(cry_args) > 2:
            """
            <Python>   reduce(foo, alist, 10)
            <Crystal>  alist.reduce(10) { |*args| foo(*args) }
            """
            return "%s.%s(%s) %s" % (cry_args[1], func, cry_args[2], block)
        else:
            """
            <Python>   reduce(foo, alist)
            <Crystal>  alist.reduce { |*args| foo(*args) }
            """
            return "%s.%s %s" % (cry_args[1], func, block)


    def map(funcdb):
        """
        # map - lambda Call
        <Python>    map(lambda x: x**2, [1,2])
        <Crystal>   [1, 2].map{|x| x**2}
        # map - block
        <Python>    map(foo, [1, 2])
        <Crystal>   [1, 2].map{|_| foo(_) } 
        """
        cv = funcdb.crystal_visitor
        cry_args = funcdb.crystal_args
        node = funcdb.node
        func = funcdb.funcstr
        if isinstance(node.args[0], ast.Lambda):
            block = cv.visit_Lambda(node.args[0], style="block")
            return "%s.%s %s" % (cry_args[1], func, block)
        else:
            return "%s.%s {|v| %s(v)}" % (cry_args[1], func, cry_args[0])

    def tuple(funcdb):
        """ 
        <Python>    tuple(range(3))
        <Crystal>   3.times.to_a
        """
        cry_args_s = ' '.join(funcdb.crystal_args)
        if len(funcdb.node.args) == 0:
            return "Tuple.new()"
        elif (len(funcdb.node.args) == 1) and isinstance(funcdb.node.args[0], ast.Str):
            return "%s.split(\"\")" % (cry_args_s)
        else:
            return "%s.to_a" % (cry_args_s)

    def list(funcdb):
        """ 
        <Python>    list(range(3))
        <Crystal>   3.times.to_a
        """
        cry_args_s = ' '.join(funcdb.crystal_args)
        if len(funcdb.node.args) == 0:
            return funcdb.empty_list()
        elif (len(funcdb.node.args) == 1) and isinstance(funcdb.node.args[0], ast.Str):
            return "%s.split(\"\")" % (cry_args_s)
        else:
            return "%s.to_a" % (cry_args_s)
        
    def dict(funcdb):
        """ 
        <Python>    dict([('foo', 1), ('bar', 2)])
        <Crystal>   {'foo' => 1, 'bar' => 2}
        """
        cv = funcdb.crystal_visitor
        if len(funcdb.node.args) == 0:
            return funcdb.empty_hash()
        elif len(funcdb.node.args) == 1:
            if isinstance(funcdb.node.args[0], ast.List):
                cry_args = []
                for elt in funcdb.node.args[0].elts:
                    cv._tuple_type = '=>'
                    cry_args.append(cv.visit(elt))
                    cv._tuple_type = '[]'
            elif isinstance(funcdb.node.args[0], ast.Dict):
                return cry_args[0]
            elif isinstance(funcdb.node.args[0], ast.Name):
                return "%s.dup" % cry_args[0]
        else:
            cv.set_result(2)
            raise CrystalError("dict in argument list Error")
        return "{%s}" % (", ".join(cry_args))
