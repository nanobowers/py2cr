#! /usr/bin/env python

from typing import Tuple, Optional, List, Dict
from enum import Enum

import ast
import inspect
import sys
import os.path
import argparse
import re
import glob
import copy
from collections import OrderedDict
from pprint import pprint

# local code
from . import formatter
from . import types

# function/attribute "translators"
from .translator import *
from . import pymain
from . import pyos
from . import pysys
from . import pysix
from . import pycopy
from . import numpy
from .errors import CrystalError

registry = TranslatorRegistry()
#debug print(registry.map_name_to_klass)

###############################
try:
    ast.Constant()
except NameError:
    # python 3.5 doesnt have ast.Constant, which will cause failures later on
    # so we define a dummy class/constant here.
    ast.Constant = type('Constant', (object,), dict())

# NOTE: Scope is used as a decorator (@scope)
def scope(func):
    func.scope = True
    return func

class OperationMode(Enum):
    STOP = 0 # default
    WARNING = 1  # for all script mode
    NO_ERROR = 2 # for module mode

class ResultStatus(Enum):
    OK = 0
    INCLUDE_WARNING = 1
    INCLUDE_ERROR = 2

class FuncCall:
    def __init__(self, cryvisit, node, crytype):
        self.crystal_visitor = cryvisit
        self.node = node
        self.crytype = crytype
        self.crystal_args = [ self.crystal_visitor.visit(_arg) for _arg in self.node.args ]
        self.funcstr = None
        self.func_module = ""
        self.func_name = None

    def set_func(self, funcstr):
        self.funcstr = funcstr
        funclist = funcstr.split('.')
        if len(funclist) == 0:
            raise Exception(f"Cannot accept empty funclist '{funcstr}'")
        elif len(funclist) == 1:
            self.func_module = ""
            self.func_name = funclist[0]
        else:
            self.func_module = ".".join(funclist[0:-1])
            self.func_name = funclist[-1]

    def empty_list(self):
        return self.crystal_visitor.empty_list(self.node, self.crytype)

    def empty_hash(self):
        return self.crystal_visitor.empty_hash(self.node, self.crytype)

    def wrap_class_method(self, cls, method):
        argstr = ", ".join(self.crystal_args)
        return "%s.%s(%s)" % (cls, method, argstr)

class RB(object):

    # python 3
    name_constant_map = {
        True  : 'true',
        False : 'false',
        None  : 'nil',
    }
    func_name_map = {
        'zip'   : 'py_zip',
        'set'   : 'Set.new',
        'print' : 'py_print',
        'open'  : 'File.open',
        'bool'   : 'py_is_bool', # bool-type-cast
    }
    name_map = {
        'True'  : 'true',  # python 2.x
        'False' : 'false', # python 2.x
        'None'  : 'nil',   # python 2.x
        'str'   : 'String',
        'int'   : 'Int32',
        'float' : 'Float64',
        'list'  : 'Array',
        'tuple' : 'Tuple',
        'dict'  : 'Hash',
        'bytes' : 'Bytes',
        '__file__' : '__FILE__',
    }

    #
    # Many of Python's runtime errors do not have any equivalent
    # in crystal, as Crystal moves the error from runtime to compile-time
    # Hence, many of these python exceptions are commented out.
    #
    exception_map = {
        #'NotImplementedError' : 'NotImplementedError',
        #'StopIteration'       : 'StopIteration',
        #'TypeError'           : 'ArgumentError',
        #'ValueError'          : 'ArgumentError',
        'AssertionError'      : 'AssertionError', # assert => raise
        #'AttributeError'      : 'NoMethodError',
        'Exception'           : 'Exception',
        #'EOFError'            : 'EOFError',
        #'FloatingPointError'  : '???',
        #'GeneratorExit'       : '???',
        #'ImportError'         : 'LoadError',
        'IndexError'          : 'IndexError', # same
        #'IndentationError'    : '???',  # no crystal equiv
        'KeyError'            : 'KeyError', # same
        'KeyboardInterrupt'   : 'Interrupt',
        'LookupError'         : '???',
        'MemoryError'         : 'NoMemoryError',
        'ModuleNotFoundError' : 'LoadError',
        'NameError'           : 'NameError',
        'NotImplementedError' : 'NotImplementedError',
        'OSError'             : 'IOError',
        'OverflowError'       : 'OverflowError',
        'RecursionError'      : 'SystemStackError',
        'ReferenceError'      : 'ReferenceError',
        'RuntimeError'        : 'RuntimeError',
        #'StopIteration'       : '???',
        #'SyntaxError'         : '???',  # fail at compile
        #'SystemError'         : 'ScriptError',
        #'SystemExit'          : 'SystemExit',
        #'TabError'            : '???',  # no equiv in crystal
        #'TypeError'           : '???',  # fail at compile
        #'UnboundLocalError'   : '???',  # fail at compile
        #'UnicodeEncodeError'  : '???',  # fail at compile
        #'UnicodeDecodeError'  : '???',  # fail at compile
        #'UnicodeTranslateError' : '???',  # fail at compile
        #'ValueError'          : '???',  # fail at compile
        'ZeroDivisionError'   : 'DivisionByZeroError',

    }

    # isinstance(foo, String) => foo.is_a?(String)
    methods_map_middle = {
        'isinstance' : 'is_a?',  # only valid at compile-time in Crystal
        'all' : 'py_all?',
        'any' : 'py_any?',
        'remove': 'py_remove',
        # probably should remove these:
        'hasattr'    : 'instance_variable_defined?',
        'getattr': 'py_getattr',
    }

    # np.array([x1, x2]) => Numo::NArray[x1, x2]
    order_methods_with_bracket : Dict[str, str] = {}

    methods_map : Dict[str, str] = {}
    ignore : Dict[str, str] = {}
    mod_class_name : Dict[str, str] = {}
    order_inherited_methods : Dict[str, str] = {}

    # float(foo) => foo.to_f
    reverse_methods = {
        'type'  : 'class',
        'abs'   : 'abs',            # Numeric
        'chr'   : 'chr',            # Int to Unicode char
        'bin'   : 'to_s(2)',
        'oct'   : 'to_s(8)',
        'hex'   : 'to_s(16)',
        'len'   : 'size',
     # moved to pymain to handle empty-case
     #   'int'   : 'to_i',
     #   'float' : 'to_f',
     #   'str'   : 'to_s',
     # moved to minmax-like for special multi-scalar case
     #   'max'   : 'max',            # Array
     #   'min'   : 'min',            # Array
        'all'   : 'is_all?',        # Enumerable
        'any'   : 'is_any?',        # Enumerable
        'iter'  : 'each',
        'sum'   : 'sum', # if Ruby 2.3 or before is 'inject(:+)' method.
        #'sum'   : 'inject(:+)', # if Ruby 2.4 or later is better sum() method.
        'round' : 'round',
    }
    minmax_like_methods = {
        'max'   : 'max',            # Array
        'min'   : 'min',            # Array
    }

    attribute_map = {
        # String
        'count'      : 'py_count',
        'upper'      : 'upcase',
        'lower'      : 'downcase',
        'endswith'   : 'ends_with?',
        'startswith' : 'starts_with?',
        'replace'    : 'py_replace', # could distinguish gsub case if we were based on #-args.

        'zip'        : 'py_zip',
        'find'       : 'py_find',
        'rfind'      : 'py_rfind',
        'split'      : 'py_split',
        'strip'      : 'py_strip',
        'lstrip'     : 'py_lstrip',
        'rstrip'     : 'py_rstrip',

        'append'   : 'push',        # Array
        'sort'     : 'sort!',       # Array
        'reverse'  : 'reverse!',    # Array
        'extend'   : 'concat',      # Array
        'items'    : 'to_a',        # Hash
        'write'    : 'print',       # IO
        'read'     : 'py_read',     # IO
    }
    attribute_not_arg = {
        'split'   : 'split',         # String
        'splitlines': 'split("\n")', # String
    }
    attribute_with_arg = {
        'split'   : 'py_split',       # String
    }

    call_attribute_map = set([       # Array
        'join',
    ])

    list_map   = set(['list']) # Array
    tuple_map  = set(['tuple']) # Tuple
    dict_map   = set(['dict']) # Hash
    iter_map   = set(['map'])
    reduce_map = set(['reduce'])
    range_map  = set(['range','xrange'])

    bool_op = {
        'And'    : '&&',
        'Or'     : '||',
    }

    unary_op = {
        'Invert' : '~',
        'Not'    : '!',
        'UAdd'   : '+',
        'USub'   : '-',
    }

    binary_op = {
        'Add'    : '+',
        'Sub'    : '-',
        'Mult'   : '*',
        'Div'    : '/',
        'FloorDiv' : '//',
        'Mod'    : '%',
        'LShift' : '<<',
        'RShift' : '>>',
        'BitOr'  : '|',
        'BitXor' : '^',
        'BitAnd' : '&',
    }

    comparison_op = {
            'Eq'    : "==",
            'NotEq' : "!=",
            'Lt'    : "<",
            'LtE'   : "<=",
            'Gt'    : ">",
            'GtE'   : ">=",
            'Is'    : "===",
        }

    # Verbose-print macro
    def vprint(self, message : str) -> None:
        if self._verbose:
            print("#>> " + message)

    def maybewarn(self, message : str) -> None:
        if self._mode == OperationMode.WARNING:
            self.set_result(ResultStatus.INCLUDE_WARNING)
            sys.stderr.write("Warning : " + message + "\n")

    # Error Stop Mode
    def mode(self, mode):
        self._mode = mode

    # Convert Status
    def set_result(self, result):
        if self._result < result:
            self._result = result

    def get_result(self):
        return self._result

    def __init__(self, path='', dir_path='', base_path_count=0, mod_paths = None, verbose = False):
        self._verbose = verbose
        self._mode = OperationMode.STOP # Error Stop Mode : 0:stop(default), 1:warning(for all script mode), 2:no error(for module mode)
        self._result = ResultStatus.OK # Convert Status : 0:No Error, 1:Include Warning, 2:Include Error
        paths = [formatter.capitalize(x) for x in path.split('/')]
        self._dir_path = dir_path
        self._path = []
        for p in paths:
            if p != '__init__':
                self._path.append(p)
        self._base_path_count = base_path_count
        self._module_functions = []
        self._is_module = False
        self.mod_paths = mod_paths or {}
        self._rel_path = []
        for rel_path in self.mod_paths.values():
            self._rel_path.append(rel_path.replace('/', '.'))

        self.vprint("base_path_count[%s] dir_path: %s, path : %s : %s" % (self._base_path_count, dir_path, path, self._path))
        self.vprint("mod_paths : %s" % self.mod_paths)

        self.__formatter = formatter.Formatter()
        #self.capitalize = self.__formatter.capitalize
        self.write = self.__formatter.write
        self.read = self.__formatter.read
        self.clear = self.__formatter.clear
        self.indent = self.__formatter.indent
        self.dedent = self.__formatter.dedent
        self.indent_string = self.__formatter.indent_string
        self.dummy = 0
        self.classes = ['dict', 'list', 'tuple']
        # This is the name of the class that we are currently in:
        self._class_name = None
        # This is the name of the crystal class that we are currently in:
        self._rclass_name = None

        # This is use () case of the tuple that we are currently in:
        #   '()'   :  "(a, b)"
        #   '[]'   :  "[a, b]"
        #   '=>'   :  "%s => %s" (Hash)
        #   ''     :  'a, b'
        self._tuple_type = '[]'
        self._func_args_len = 0
        self._dict_format = False # True : Symbol ":", False : String "=>"

        self._is_string_symbol = False # True : ':foo' , False : '"foo"'

        # This lists all variables in the local scope:
        self._scope = []

        #All calls to names within _class_names will be preceded by 'new'
        # Python original class name
        self._class_names = set()

        # Crystal class name (first character is Capitalized)
        self._rclass_names = set()
        self._classes = {}

        # This lists all inherited class names:
        self._classes_base_classes = {}

        # This lists all function names:
        self._function = []

        # This lists all arguments in a function:
        self._function_args = []
        self._functions = {}
        self._functions_rb_args_default = {}

        # This lists all instance functions in the class scope:
        self._self_functions = []
        self._classes_self_functions = {}
        self._self_functions_args = {}
        self._classes_self_functions_args = {}

        # This lists all static functions (Crystal's class method) in the class scope:
        self._class_functions = []
        self._classes_functions = {}
        self._class_functions_args = {}
        self._classes_class_functions_args = {}

        # This lists all static variables (Crystal's class variables) in the class scope:
        self._class_variables = []
        self._classes_variables = {}

        # This lists all instance variables (Crystal's class variables) in the class scope:
        self._class_self_variables = []

        # This lists all lambda functions:
        self._lambda_functions = []

        # This is a mapping of module-name when "import foo as bar" is used.
        self._module_aliases : Dict[str,str] = {}

        self._import_files = []
        self._imports = []
        self._call = False
        self._conv = True # use YAML convert case.

    def new_dummy(self):
        dummy = "__dummy%d__" % self.dummy
        self.dummy += 1
        return dummy

    def name(self, node):
        return node.__class__.__name__

    def get_bool_op(self, node) -> str:
        return self.bool_op[node.op.__class__.__name__]

    def get_unary_op(self, node) -> str:
        return self.unary_op[node.op.__class__.__name__]

    def get_binary_op(self, node) -> str:
        return self.binary_op[node.op.__class__.__name__]

    def get_comparison_op(self, node) -> str:
        return self.comparison_op[node.__class__.__name__]

    def visit(self, node, scope=None, crytype=None):

        if self._mode == OperationMode.NO_ERROR:
            node_name = self.name(node)
            if node_name not in ['Module', 'ImportFrom', 'Import', 'ClassDef', 'FunctionDef', 'Name', 'Attribute']:
                return ''

        try:
            visitor = getattr(self, 'visit_' + self.name(node))
        except AttributeError as exc:
            if self._mode == OperationMode.STOP:
                self.set_result(ResultStatus.INCLUDE_ERROR)
                raise CrystalError("Syntax not supported (%s line:%d col:%d)" % (node, node.lineno, node.col_offset)) from exc
            else:
                self.maybewarn("Syntax not supported (%s line:%d col:%d)" % (node, node.lineno, node.col_offset))
                return ''

        if hasattr(visitor, 'statement'):
            return visitor(node, scope)
        elif self.name(node) in ["Dict", "List", "Call"]:
            # Do Call for handling empty dict() and list()
            return visitor(node, crytype=crytype)
        else:
            return visitor(node)

    def visit_Module(self, node):
        """
        Module(stmt* body)
        """
        self._module_functions = []
        if self._path != ['']:
            # 
            # <Python> imported/moduleb.py
            # <Crystal>   module Imported (base_path_count=0)
            #            module Moduleb (base_path_count=1)
            for i in range(len(self._path)):
                self.vprint("base_path_count : %s, i : %s" % (self._base_path_count, i))
                if i < self._base_path_count:
                    continue
                p = self._path[i]
                self.vprint("p : %s" % p)
                self.write("module %s" % p)
                self._is_module = True
                self.indent()

        for stmt in node.body:
            self.visit(stmt)

        if self._path != ['']:
            if self._module_functions:
                self.write("module_function %s" % ', '.join([':' + x for x in self._module_functions]))
            for i in range(len(self._path)):
                if i < self._base_path_count:
                    continue
                self.dedent()
                self.write("end")

    @scope
    def visit_FunctionDef(self, node):
        """ [Function Define] :
        FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns)
        """

        self._function.append(node.name)
        self._function_args = []
        is_static = False
        is_closure = False
        is_property = False
        is_setter = False
        if node.decorator_list:
            if self._class_name:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "classmethod":
                            is_static = True
                        elif decorator.id == "staticmethod":
                            is_static = True
                        elif decorator.id == "property":
                            is_property = True
                            #<Python>    @property
                            #            def x(self):
                            #                return self._x
                            #<Crystal>   def x
                            #                @_x
                            #            end

                        else:
                            self.maybewarn("Decorators are not supported : %s" % self.visit(decorator.id))
                    if isinstance(decorator, ast.Attribute):
                        if self.visit(node.decorator_list[0]) == (node.name + ".setter"):
                            is_setter = True
                            #<Python>    @x.setter
                            #            def x(self, value):
                            #                self._x = value
                            #<Crystal>   def x=(val)
                            #              @_x=val
                            #            end

                if not is_static and not is_property and not is_setter:
                    self.maybewarn("Decorators are not supported : %s" % self.visit(node.decorator_list[0]))

        #for a in node.args.args:
        #    print(a.annotation.id)

        defaults = [None]*(len(node.args.args) - len(node.args.defaults)) + node.args.defaults
        # Class Method
        if self._class_name:
            self._scope = [arg.arg for arg in node.args.args]

        # get key for not keyword argument Call.
        rb_args_default = []
        # set normal and keyword argument Call.
        rb_args = []
        for arg, default in zip(node.args.args, defaults):

            arg_id = arg.arg

            argxlist = [arg_id]
            if arg.annotation:
                argxlist.append(":")
                anno = types.CrystalTypes(arg.annotation)
                argxlist.append(anno.visit())

            if default is None:
                rb_args_default.append(None)
            else:
                argxlist.append("=")
                argxlist.append(self.visit(default))
                rb_args_default.append(arg_id)
            rb_args.append(" ".join(argxlist))

        # [Function method argument with Multiple Variables] :
        # <Python>    def foo(fuga, hoge):
        #             def bar(fuga, hoge, *piyo):
        # <Crystal>   def foo(fuga, hoge)
        #             def bar(fuga, hoge, *piyo)
        #
        # [Class instance method] :
        # <Python>    class foo:
        #                 def __init__(self, fuga):
        #                 def bar(self, hoge):
        # <Crystal>   class Foo
        #                 def initialize(fuga)
        #                 def bar(hoge)
        if len(self._function) != 1:
            is_closure = True
        if '__new__' == node.name:
            func_name = 'new'
        elif self._class_name:
            if not is_static and not is_closure:
                if not rb_args[0] == "self":
                    raise NotImplementedError(f"The first argument must be 'self' in line {node.lineno}")
                del rb_args[0]
                del rb_args_default[0]

        if '__init__' == node.name:
            func_name = 'initialize'
        elif '__call__' == node.name:
            func_name = 'call'
        elif '__str__' == node.name:
            func_name = 'to_s'
        elif is_static:
            #If method is static, we also add it directly to the class method
            func_name = "self." + node.name
        else:
            # Function Method
            func_name = node.name

        # star arguments
        if node.args.vararg:
            vararg = "*%s" % self.visit(node.args.vararg)
            rb_args.append(vararg)
            rb_args_default.append([None])

        # keyword only arguments
        for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            arg_id = arg.arg
            rb_args.append("%s = %s" % (arg_id, self.visit(default)))
            rb_args_default.append(arg_id)

        # double star arguments
        if node.args.kwarg:
            kwarg = "**%s" % self.visit(node.args.kwarg)
            rb_args.append(kwarg)
            rb_args_default.append([])
        self._function_args = rb_args
        rb_args = ", ".join(rb_args)
        if self._class_name is None:
            self._functions[node.name] = rb_args_default
        else:
            self._functions_rb_args_default[node.name] = rb_args_default

        if is_setter:
            if self._is_module and not self._class_name:
                self._module_functions.append(func_name)
                #self.write("def self.%s=(%s)" % (func_name, rb_args))
            #else:
            #    self.write("def %s=(%s)" % (func_name, rb_args))
            self.write("def %s=(%s)" % (func_name, rb_args))
        elif is_closure:
            # [function closure] :
            #<Python> def foo(fuga):
            #             def bar(fuga):
            #
            #             bar()
            #<Crystal>   def foo(fuga)
            #              bar = lambda do |fuga|
            #              end
            #              bar.()
            #            end
            if len(self._function_args) == 0:
                self.write("%s = -> do" % func_name)
            else:
                self.write("%s = ->(%s) do" % (func_name, rb_args))
            self._lambda_functions.append(func_name)
        else:
            if self._is_module and not self._class_name:
                self._module_functions.append(func_name)
                #self.write("def self.%s(%s)" % (func_name, rb_args))
            #else:
            #    self.write("def %s(%s)" % (func_name, rb_args))
            ## Adding support for annotated return-type
            if node.returns:
                anno = types.CrystalTypes(node.returns).visit()
                self.write("def %s(%s) : %s" % (func_name, rb_args, anno))
            else:
                self.write("def %s(%s)" % (func_name, rb_args))

        if self._class_name is None:
            self._scope = [arg.arg for arg in node.args.args]
            self._scope.append(node.args.vararg)

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write('end')

        if self._class_name:
            self._scope = []
        else:
            if node.decorator_list:
                # [method argument set Method Object] :
                #<Python> @mydecorator
                #         def describe():
                #             pass
                #<Crystal>   def describe()
                #            end
                #            describe = mydecorator(method(:describe))
                if len(node.decorator_list) == 1 and \
                    isinstance(node.decorator_list[0], ast.Name):
                    self.write('%s = %s(method(:%s))' % (node.name, node.decorator_list[0].id, node.name))
                    #self.write('%s = %s(%s)' % (node.name, node.decorator_list[0].id, node.name))
                    self._scope.append(node.name)

        self._function.pop()
        self._function_args = []

    @scope
    def visit_ClassDef(self, node):
        """
        [Class Define] :
        ClassDef(identifier name,expr* bases, keyword* keywords, stmt* body,expr* decorator_list)
        """
        self._self_functions = []
        self._functions_rb_args_default = {}
        self._class_functions = []
        self._class_variables = []
        self._class_self_variables = []
        self._self_functions_args = {}
        self._class_functions_args = {}

        # [Inherited Class Name convert]
        # <Python> class Test(unittest.TestCase): => <Crystal> class Test < Test::Unit::TestCase
        bases = [self.visit(n) for n in node.bases]
        # no use Object class
        if 'Object' in bases:
            bases.remove('Object')
        if 'object' in bases:
            bases.remove('object')

        self.vprint("bases : %s" % bases)

        # [Inherited Class Name]
        base_classes = []
        base_rclasses = []
        for base in bases:
            if base in self.mod_class_name.keys():
                base_rclasses.append(self.mod_class_name[base])
            else:
                base_rclasses.append(base)

            if base in self._classes_base_classes:
                inherited_bases = self._classes_base_classes[base]
                inherited_bases.append(base)
            else:
                inherited_bases = [base]
            for i_base in inherited_bases:
                if i_base not in base_classes:
                    base_classes.append(i_base)

        self.vprint("ClassDef class_name[%s] base_classes: %s base_rclasses: %s" % (node.name, base_classes, base_rclasses))

        self._class_name = node.name
        self._classes_base_classes[node.name] = base_classes

        # [Inherited Class Name] <Python> class foo(bar) => <Crystal> class Foo < Bar
        bases = [cls[0].upper() + cls[1:] for cls in base_rclasses]

        if not bases:
            bases = []

        # self._classes remembers all classes defined
        self._classes[node.name] = node
        self._class_names.add(node.name)

        # [Class Name]  <Python> class foo: => <Crystal> class Foo
        class_name = node.name
        rclass_name = class_name[0].upper() + class_name[1:]

        self.vprint("ClassDef class_name[%s] bases: %s" % (node.name, bases))

        if len(bases) == 0:
            self.write("class %s" % (rclass_name))
        elif len(bases) == 1:
            self.write("class %s < %s" % (rclass_name, bases[-1]))
        else:
            sys.stderr.write("Multiple inheritance is not supported : class_name[%s] < super class %s\n" % (node.name, bases))
            self.write("class %s < %s # %s" % (rclass_name, bases[-1], bases[0:-1]))
        self.indent()
        self._rclass_name = rclass_name
        self._rclass_names.add(rclass_name)

        #from ast import dump
        #~ methods = []
        # set instance method in the class
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                if len(stmt.decorator_list) == 1 and \
                    isinstance(stmt.decorator_list[0], ast.Name) and \
                    stmt.decorator_list[0].id == "staticmethod":
                    self._class_functions.append(stmt.name)
                else:
                    self._self_functions.append(stmt.name)
        if len(self._class_functions) != 0:
            # for staticmethods, also define an instance method
            for clsfuncname in self._class_functions:
                self.write("# instance-method from @staticmethod")
                self.write("def %s(*args,**kwargs)" % clsfuncname)
                self.indent()
                self.write("self.class.%s(*args,**kwargs)" % clsfuncname)
                self.dedent()
                self.write("end")

        self._classes_functions[node.name] = self._class_functions
        self.vprint("self._self_functions : %s" % self._self_functions)
        self.vprint("self._classes_self_functions : %s" % self._classes_self_functions)
        self._classes_self_functions[node.name] = self._self_functions

        for stmt in node.body:
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                # [Class Variable] :
                #<Python> class foo:
                #             x
                #<Crystal>   class Foo
                #             @@x 
                # ast.Tuple, ast.List, ast.*
                value = self.visit(stmt.value)
                #if isinstance(stmt.value, (ast.Tuple, ast.List)):
                #    value = "[%s]" % self.visit(stmt.value)
                #else:
                #    value = self.visit(stmt.value)

                # Annotated assign only has a singular target
                if isinstance(stmt, ast.Assign):
                    assign_targets = stmt.targets
                else:
                    assign_targets = [stmt.target]

                for t in assign_targets:
                    #print(t)
                    var = self.visit(t)
                    self.write("@@%s = %s" % (var, value))
                    if isinstance(stmt.value, ast.List):
                        valuetype = "_"
                    else:
                        valuetype = types.CrystalTypes.constant(stmt.value)
                    self.write("@%s : %s = %s" % (var, valuetype, "nil"))
                    self._class_variables.append(var)
            else:
                self.visit(stmt)
        if len(self._functions_rb_args_default) != 0:
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef):
                    if len(stmt.decorator_list) == 1 and \
                        isinstance(stmt.decorator_list[0], ast.Name) and \
                        stmt.decorator_list[0].id == "staticmethod":
                        self._class_functions_args[stmt.name] = self._functions_rb_args_default[stmt.name]
                    else:
                        self._self_functions_args[stmt.name] = self._functions_rb_args_default[stmt.name]

        self._classes_class_functions_args[node.name] = self._class_functions_args
        self._classes_self_functions_args[node.name] = self._self_functions_args
        self._classes_variables[node.name] = self._class_variables
        self._class_name = None
        self._rclass_name = None

        for v in (self._class_variables):
            self.write("def self.%s; @@%s; end" % (v,v))
            self.write("def self.%s=(val); @@%s=val; end" % (v,v))
            self.write("def %s; @%s = @@%s if @%s.nil?; @%s; end" % (v,v,v,v,v))
            self.write("def %s=(val); @%s=val; end" % (v,v))

        #for func in self._self_functions:
        #    if func in self.attribute_map.keys():
        #        self.write("alias :%s :%s" % (self.attribute_map[func], func))
        self.dedent()
        self.write("end")
        self._self_functions = []
        self._self_functions_args = {}
        self._functions_rb_args_default = {}
        self._class_functions = []
        self._class_functions_args = {}
        self._class_variables = []
        self._class_self_variables = []

    def visit_Return(self, node):
        if node.value is None:
            self.write("return")
        else:
            self.write("return %s" % self.visit(node.value))

    def visit_Delete(self, node):
        """
        Delete(expr* targets)
        """
        idval = ''
        num = ''
        key = ''
        pyslice = ''
        attr = ''
        for stmt in node.targets:
            if isinstance(stmt, (ast.Name)):
                idval = self.visit(stmt)
            elif isinstance(stmt, (ast.Subscript)):
                if isinstance(stmt.value, (ast.Name)):
                    idval = self.visit(stmt.value)
                if isinstance(stmt.slice, (ast.Index)):
                    if isinstance(stmt.slice.value, (ast.Str)):
                        key = self.visit(stmt.slice)
                    elif isinstance(stmt.slice.value, (ast.Num)):
                        num = self.visit(stmt.slice)
                    else:
                        raise Exception("Bad stmt.slice.value in visit_Delete %s" % type(stmt.slice.value))
                elif isinstance(stmt.slice, (ast.Slice)):
                    pyslice = self.visit(stmt.slice)
                elif isinstance(stmt.slice, (ast.Constant)): #py3.9
                    if isinstance(stmt.slice.value, int):
                        num = self.visit(stmt.slice)
                    else:
                        key = self.visit(stmt.slice)
                else:
                    raise Exception("Bad stmt.slice in visit_Delete %s" % type(stmt.slice))
            elif isinstance(stmt, (ast.Attribute)):
                if isinstance(stmt.value, (ast.Name)):
                    idval = self.visit(stmt.value)
                attr = stmt.attr
            else:
                raise Exception("Bad stmt in visit_Delete %s" % type(stmt))

        if num != '':
            # <Python>    del foo[0]
            # <Crystal>   foo.delete_at[0]
            self.write(f"{idval}.delete_at({num})")
        elif key != '':
            # <Python>    del foo['hoge']
            # <Crystal>   foo.delete['hoge']
            self.write(f"{idval}.delete({key})")
        elif pyslice != '':
            # <Python>    del foo[1:3]
            # <Crystal>   py_del(foo, 1...3)
            # note that `py_del` is defined for Array/Range args.
            self.write(f"py_del({idval}, {pyslice})")
        elif attr != '':
            # <Python>    del foo.bar
            # <Crystal>   foo.instance_eval { remove_instance_variable(:@bar) }
            self.write("%s.instance_eval { remove_instance_variable(:@%s) }" % (idval, attr))
        else:
            # <Python>    del foo
            # <Crystal>   foo = nil
            self.write("%s = nil" % (idval))

        # TODO: The previous two cases ("del foo.bar", "del foo") probably dont make any sense in crystal and should be removed.


    @scope
    def visit_Assign(self, node):
        """
        Assign(expr* targets, expr value)
        """
        target_str = ''
        value = self.visit(node.value)
        for target in node.targets:
            if isinstance(target, (ast.Tuple, ast.List)):
                x = [self.visit(t) for t in target.elts]
                if len(x) == 1:
                    # Weird special case: pluck first element from array
                    # appears to work only for arrays and with a single element.
                    # <Python>   x, = [1]
                    # <Crystal>  x = [1].first
                    target_str += "%s = " % x[0]
                    value = "%s.first" % value
                else:
                    # multi assign
                    # x, y, z = [1, 2, 3]
                    target_str += "%s = " % ','.join(x)
            elif isinstance(target, ast.Subscript):
                name = self.visit(target.value)
                if isinstance(target.slice, (ast.Index, ast.Constant)):
                    # found index assignment # a[0] = xx
                    for arg in self._function_args:
                        if arg == ("**%s" % name):
                            self._is_string_symbol = True
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
                    self._is_string_symbol = False
                elif isinstance(target.slice, ast.Slice):
                    # found slice assignment
                    target_str += "%s[%s...%s] = " % (name, self.visit(target.slice.lower), self.visit(target.slice.upper))
                elif isinstance(target.slice, ast.ExtSlice):
                    # found ExtSlice assignment
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
                else:
                    self.maybewarn("Unsupported assignment type (%s) in Assign(ast.Subscript)" % self.visit(target))
                    target_str += "%s[%s] = " % (name, self.visit(target.slice))
            elif isinstance(target, ast.Name):
                var = self.visit(target)
                if not var in self._scope:
                    self._scope.append(var)
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        if node.value.func.id in self._class_names:
                            self._classes_self_functions_args[var] = self._classes_self_functions_args[node.value.func.id]
                # set lambda functions
                if isinstance(node.value, ast.Lambda):
                    self._lambda_functions.append(var)
                target_str += "%s = " % var
            elif isinstance(target, ast.Attribute):
                var = self.visit(target)
                # [instance variable] :
                # <Python>    self.foo = hoge
                # <Crystal>   @foo     = hoge
                if var == 'self':
                    target_str += "@%s = " % str(target.attr)
                    self._class_self_variables.append(str(target.attr))
                else:
                    target_str += "%s = " % var
            else:
                self.maybewarn("Unsupported assignment type (%s) in Assign" % self.visit(target))
                target_str += "%s[%s] = " % (name, self.visit(target))
        self.write("%s%s" % (target_str, value))

    def visit_AugAssign(self, node):
        """
        AugAssign(expr target, operator op, expr value)
        """
        # TODO: Make sure that all the logic in Assign also works in AugAssign
        target = self.visit(node.target)
        value = self.visit(node.value)

        if isinstance(node.op, ast.Pow):
            self.write("%s = %s ** %s" % (target, target, value))
        #elif isinstance(node.op, ast.FloorDiv):
        #    #self.write("%s = Math.floor((%s)/(%s));" % (target, target, value))
        #    self.write("%s = (%s/%s)" % (target, target, value))
        elif isinstance(node.op, ast.Div):
            if re.search(r"Numo::", target) or re.search(r"Numo::", value):
                self.write("%s = %s / %s" % (target, self.ope_filter(target), self.ope_filter(value)))
            else:
                self.write("%s = %s / %s.to_f" % (target, self.ope_filter(target), self.ope_filter(value)))
        else:
            self.write("%s %s= %s" % (target, self.get_binary_op(node), value))

    def visit_AnnAssign(self, node):
        """
        AnnAssign is an assignment with a type annotation.
        In some sense, slightly easier than Assign, b/c AnnAssign doesnt support multiple-assignment.
        AnnAssign(expr target, expr value)
        """
        # Type annotated assignments in Python.

        target = self.visit(node.target)
        if node.value:
            crytype = types.CrystalTypes(node.annotation)
            anno = crytype.visit()
            value = self.visit(node.value, crytype=crytype)
            self.write("%s : %s = %s" % (target, anno, value))

    @scope
    def visit_For(self, node):
        """
        For(expr target, expr iter, stmt* body, stmt* orelse)
        """
        if not isinstance(node.target, (ast.Name,ast.Tuple, ast.List)):
            self.set_result(ResultStatus.INCLUDE_ERROR)
            raise CrystalError("Argument decomposition in 'for' loop is not supported")
        #if isinstance(node.target, ast.Tuple):

        #print self.visit(node.iter) #or  Variable (String case)
        #if isinstance(node.iter, ast.Str):

        self._tuple_type = '()'
        for_target = self.visit(node.target)
        self._tuple_type = '[]'
        #if isinstance(node.iter, (ast.Tuple, ast.List)):
        #    for_iter = "[%s]" % self.visit(node.iter)
        #else:
        #    for_iter = self.visit(node.iter)
        # ast.Tuple, ast.List, ast.*
        for_iter = self.visit(node.iter)

        if node.orelse:
            orelse_dummy = self.new_dummy()
            self.write("%s = false" % orelse_dummy)

        ##OLD-FOR-LOOP## self.write("for %s in %s" % (for_target, for_iter))
        self.write("%s.py_each do |%s|" % (for_iter, for_target))
        self.indent()
        for stmt in node.body:
            self.visit(stmt)

        if node.orelse:
            self.write("if %s == %s[-1]" % (for_target, for_iter))
            self.indent()
            self.write("%s = true" % orelse_dummy)
            self.dedent()
            self.write("end")

        self.dedent()
        self.write("end")

        if node.orelse:
            self.write("if %s" % orelse_dummy)
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
            self.write("end")

    @scope
    def visit_While(self, node):
        """
        While(expr test, stmt* body, stmt* orelse)
        """

        if not node.orelse:
            self.write("while %s" % self.visit(node.test))
        else:
            orelse_dummy = self.new_dummy()

            self.write("%s = false" % orelse_dummy)
            self.write("while true")
            self.write("    unless %s" % self.visit(node.test))
            self.write("        %s = true" % orelse_dummy)
            self.write("        break")
            self.write("    end")

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()

        self.write("end")

        if node.orelse:
            self.write("if %s" % orelse_dummy)
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
            self.write("end")

    def visit_IfExp(self, node):
        """
        IfExp(expr test, expr body, expr orelse)
        """
        body     = self.visit(node.body)
        or_else  = self.visit(node.orelse)
        if isinstance(node.test, (ast.NameConstant, ast.Compare)):
            return "(%s) ? %s : %s" % (self.visit(node.test), body, or_else)
        else:
            return "py_is_bool(%s) ? %s : %s" % (self.visit(node.test), body, or_else)

    @scope
    def visit_If(self, node):
        """
        If(expr test, stmt* body, stmt* orelse)
        """
        if isinstance(node.test, (ast.NameConstant, ast.Compare)):
            self.write("if %s" % self.visit(node.test))
        else:
            self.write("if py_is_bool(%s)" % self.visit(node.test))

        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        if node.orelse:
            self.write("else")
            self.indent()
            for stmt in node.orelse:
                self.visit(stmt)
            self.dedent()
        self.write("end")

    @scope
    def visit_With(self, node):
        """
        With(withitem* items, stmt* body)
        """
        # <Python>    with open("hello.txt", 'w') as f:
        #                 f.write("Hello, world!")
        # <Crystal>   File.open("hello.txt", "w") {|f|
        #                 f.write("Hello, World!")
        #             }
        # <Python>    with open("hello.txt", 'r'):
        #                 print("Hello, world!")
        # <Crystal>   File.open("hello.txt", "r") {
        #                 print("Hello, world!")
        #             }
        item_str = ''
        for stmt in node.items:
            item_str += self.visit(stmt)
        self.write(item_str)
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        self.write("}")

    @scope
    def visit_withitem(self, node):
        """
        withitem = (expr context_expr, expr? optional_vars)
        This gets caled from within the `visit_With` visitor.
        """
        func = self.visit(node.context_expr)
        if isinstance(node.context_expr, (ast.Call)):
            self.visit(node.context_expr)
        if node.optional_vars is None:
            return "%s {" % func
        else:
            val = self.visit(node.optional_vars)
            return "%s {|%s|" % (func, val)

    @scope
    def visit_ExceptHandler(self, node):
        """
        <Python 3> ExceptHandler(expr? type, identifier? name, stmt* body)
        """
        # <Python> try:
        #             except AttributeError as e:
        #    <Crystal>   begin
        #             rescue e : AttributeError
        #             end
        #    <Python> try:
        #             except cuda.cupy.cuda.runtime.CUDARuntimeError as e:
        #    <Crystal>   begin
        #             rescue AttributeError
        #             end

        if node.type is None:
            self.write("rescue")
        elif node.name is None:
            self.write("rescue %s" % self.visit(node.type))
        else:
            self.write("rescue %s : %s" % (node.name, self.visit(node.type)))
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()

    # Python 3
    @scope
    def visit_Try(self, node):
        """
        Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
        """
        self.write("begin")
        self.indent()
        for stmt in node.body:
            self.visit(stmt)
        self.dedent()
        for handle in node.handlers:
            self.visit(handle)
        if len(node.finalbody) != 0:
            self.write("ensure")
            self.indent()
            for stmt in node.finalbody:
                self.visit(stmt)
            self.dedent()
        self.write("end")


    def visit_Assert(self, node):
        """
        Assert(expr test, expr? msg)
        """
        test = self.visit(node.test)

        if node.msg is not None:
            self.write("raise AssertionError.new(%s) unless %s" % (self.visit(node.msg), test))
        else:
            self.write("raise AssertionError.new unless %s" % test)

    def visit_Import(self, node):
        """
        Import(alias* names)

        e.g.
        <python> import imported.submodules.submodulea
        <crystal>   require_relative 'imported/submodules/submodulea'
        Module(body=[Import(names=[alias(name='imported.module', asname='abc')])])

        <python> import imported.submodules.submodulea (with foo.py, bar.py)
        <crystal>   require_relative 'imported/submodules/submodulea/foo'
                 require_relative 'imported/submodules/submodulea/bar'

        * Case 1. import module
        <python> * tests/modules/import.py
                   import imported.moduleb
                   foo.moduleb_fn()
                   mb = foo.moduleb_class()
        <crystal>   * tests/modules/import_as_module.cr
                   require_relative 'imported/moduleb'
                   Imported::Moduleb::moduleb_fn()
                   mb = Imported::Moduleb::Moduleb_class.new()
        * Case 2. import module with alias
        <python> * tests/modules/import_as_module.py
                   import imported.moduleb as foo
                   foo.moduleb_fn()
                   mb = foo.moduleb_class()
        <crystal>   * tests/modules/import_as_module.cr
                   require_relative 'imported/moduleb'
                   Foo = Imported::Moduleb
                   Foo::moduleb_fn()
                   mb = Foo::Moduleb_class.new()
        """
        mod_name = node.names[0].name



        if registry.require_lookup_or_none(mod_name):

            self.vprint(f"Import mod_name={mod_name} mod_paths={self.mod_paths} **found-in-registry**")

            mod_name = node.names[0].name.replace('.', '/')
            for path, rel_path in self.mod_paths.items():
                self.vprint("Import mod_name=%s rel_path=%s" % (mod_name, rel_path))
                if (rel_path.startswith(mod_name + '/') or mod_name.endswith(rel_path)) and os.path.exists(path):
                    self._import_files.append(os.path.join(self._dir_path, rel_path).replace('/', '.'))
                    self.vprint("Import self._import_files: %s" % self._import_files)
                    self.write(f'require "./{rel_path}"')

            if node.names[0].asname is not None:
                if node.names[0].name in self._import_files:
                    base = '::'.join([formatter.capitalize(x) for x in node.names[0].name.split('.')[self._base_path_count:]])
                    self.write("%s = %s" % (node.names[0].asname.capitalize(), base))
                    self._import_files.append(node.names[0].asname)
                # No Use
                #elif node.names[0].name in self._class_names:
                #    self.write("%s = %s" % (self.capitalize(node.names[0].asname), self.capitalize(node.names[0].name)))
                #    self._class_names.add(node.names[0].asname)
                #    self._classes_self_functions_args[node.names[0].asname] = self._classes_self_functions_args[node.names[0].name]
                #else:
                #    self.write("alias %s %s" % (node.names[0].asname, node.names[0].name))

                mod_as_name = node.names[0].asname or mod_name
                self.vprint(f"Aliasing {mod_as_name} to {mod_name}")
                self._module_aliases[mod_as_name] = mod_name

            #return

        #>> module foo as otherfoo

        #>> get module's crystal name alias

        require_name = registry.require_lookup(mod_name)


        if require_name:
            if not node.names[0].name in self._imports:
                self.write(f'require "{require_name}"')
                self._imports.append(node.names[0].name)

#        for method_key, method_value in self.module_map[mod_name].items():
#            if method_value is None:
#                continue
#            if method_key == 'mod_name':
#                continue
#
#            if method_key == 'id':
#                if not node.names[0].name in self._imports:
#                    self.write("require \"%s\"" % method_value)
#                    self._imports.append(node.names[0].name)
#            elif method_key in ('range_map', 'dict_map'):
#                for key, value in method_value.items():
#                    mod_org_method = f"{mod_as_name}.{key}"
#                    RB.__dict__[method_key].add(mod_org_method)
#            #elif method_key == 'order_inherited_methods':
#            #    # no use mod_as_name (Becase Inherited Methods)
#            #    for key, value in method_value.items():
#            #        RB.__dict__[method_key][key] = value
#            else: # method_key == 'methods_map', etc..
#                for key, value in method_value.items(): # method_value: {'array':, 'prod': .. }
#                    mod_org_method = f"{mod_as_name}.{key}"
#                    RB.__dict__[method_key][mod_org_method] = value
#                    if isinstance(RB.__dict__[method_key][mod_org_method], dict):
#                        RB.__dict__[method_key][mod_org_method]['mod'] = _mod_name + '::'

    def visit_ImportFrom(self, node):
        """
        ImportFrom(identifier? module, alias* names, int? level)

        e.g.
        * Case 1. import function
          <python> * tests/modules/import.py
                     from modules.modulea import modulea_fn
                     modulea_fn()
                   * tests/modules/imported/modulea.py
                     def modulea_fn():
          <crystal>   * tests/modules/import.cr
                     require_relative 'imported/modulea'
                     include Imported::Modulea
                     modulea_fn()
                   * tests/modules/imported/modulea.cr
                     module Imported
                       module Modulea
                         def modulea_fn()
          Module(body=[ImportFrom(module='modules.modulea', names=[ alias(name='modulea_fn', asname=None)], level=0)])

        * Case 2. import function with alias
          <python> * tests/modules/import_alias.py
                     from imported.alias_fns import foo as bar
                     bar()
                   * tests/modules/imported/alias_fns.py
                     def foo():
          <crystal>   * tests/modules/import_alias.cr
                     require_relative 'imported/alias_fns'
                     include Imported::Alias_fns
                     alias bar foo
                     bar()
                   * tests/modules/imported/alias_fns.cr
                     module Imported
                       module Alias_fns
                         def foo()
                         end
                         module_function :foo
          Module(body=[ImportFrom(module='imported.alias_fns', names=[ alias(name='foo', asname='bar')], level=0)])

        * Case 3. import module
          <Python> * tests/modules/imported/modulee.py
                     from imported.submodules import submodulea
                     def bar():
                         submodulea.foo()
                   * tests/modules/imported/submodules/submodulea.py
                     def foo():
          <Crystal>   * tests/modules/imported/modulee.cr
                     module Imported
                       module Modulee
                         require_relative 'submodules/submodulea'
                         include Imported::Submodules
                         def bar()
                           Submodulea::foo()
                   * tests/modules/imported/submodules/submodulea.cr
                     module Imported
                       module Submodules
                         module Submodulea
                           def foo()

        * Case 4. import module with alias
          <Python> * tests/modules/from_import_as_module.py
                     from imported import moduleb as foo
                     foo.moduleb_fn()
                   * tests/modules/imported/moduleb.py
                     def moduleb_fn():
          <Crystal>   * tests/modules/imported/modulee.cr
                     require_relative 'imported/moduleb'
                     include Imported
                     Foo = Moduleb
                     Foo::moduleb_fn()
                   * tests/modules/imported/moduleb.cr
                     module Imported
                       module Moduleb
                         def moduleb_fn()

        * Case 5. import class with alias
          <python> * tests/modules/import_alias.py
                     from imported.alias_classes import spam as eggs
                     e = eggs()
                   * tests/modules/imported/alias_classes.py
                     class spam:
          <crystal>   * tests/modules/import_alias.cr
                     require_relative 'imported/alias_classes'
                     include Imported::Alias_fns
                     Eggs = Spam
                     e = Eggs.new()
                   * tests/modules/imported/alias_classes.cr
                     module Imported
                       module Alias_classes
                         class Spam
        """
        self.vprint(f"mod_paths : {self.mod_paths}")

        if node.module is not None and not registry.require_lookup_or_none(node.module):

            require_name = registry.require_lookup(node.module)
            self._import_files.append(node.module)
            mod_name = node.module.replace('.', '/')
            mod_name_i = node.module.replace('.', '/') + '/' + node.names[0].name
            # from imported.submodules import submodulea
            # => require_relative 'submodules/submodulea'

            self.vprint("ImportFrom mod_name : %s mod_name_i: %s" % (mod_name , mod_name_i))
            for path, rel_path in self.mod_paths.items():
                self.vprint("ImportFrom mod_name : %s rel_path : %s" % (mod_name, rel_path))
                if node.names[0].name != '*':
                    if path.endswith(mod_name_i + '.py'):
                        self.write("require \"%s\"" % rel_path)
                        dir_path = os.path.relpath(mod_name, self._dir_path)
                        if dir_path != '.':
                            self._import_files.append(os.path.relpath(rel_path, dir_path).replace('/', '.'))
                        else:
                            self._import_files.append(rel_path.replace('/', '.'))
                        self.vprint("ImportFrom self._import_files: %s" % self._import_files)
                        break
                if path.endswith(mod_name + '.py'):
                    self.write("require \"%s\"" % rel_path)
                    break
            else:
                if require_name is not None:
                    self.write("require \"%s\"" % require_name)
            base = '::'.join([formatter.capitalize(x) for x in node.module.split('.')[self._base_path_count:]])
            # self.write("#include %s" % base)

            if node.names[0].asname is not None:
                if node.names[0].name in self._import_files:
                    base = '::'.join([formatter.capitalize(x) for x in node.names[0].name.split('.')[self._base_path_count:]])
                    self.write("%s = %s" % (formatter.capitalize(node.names[0].asname), base))
                    self._import_files.append(node.names[0].asname)
                elif node.names[0].name in self._class_names:
                    self.write("%s = %s" % (formatter.capitalize(node.names[0].asname), formatter.capitalize(node.names[0].name)))
                    self._class_names.add(node.names[0].asname)
                    self._classes_self_functions_args[node.names[0].asname] = self._classes_self_functions_args[node.names[0].name]
                else:
                    self.write("#alias %s %s" % (node.names[0].asname, node.names[0].name))
            return

        
        #<Python>     from numpy import array
        #             array([1, 1])
        #<Crystal>    require "numo/narray"
        #             include Numo
        #             NArray[1, 1]
        #ImportFrom(module='numpy', names=[ alias(name='array', asname=None)], level=0),
        #Expr( value= Call(
        #      func= Name(id='array', ctx= Load()),
        #      args=[ List(elts=[ Num(n=1), Num(n=1)], ctx= Load())], keywords=[]))

        require_name = registry.require_lookup(node.module)

        self.vprint("REQUIRE #{require_name}")

        if require_name:
            if node.module not in self._imports:
                self.write(f'require "{require_name}"')
                self._imports.append(node.module)
        return

#        if node.module not in self.module_map:
#            return
#        _mod_name = self.module_map[node.module].get('mod_name', '')
#
#        for method_key, method_value in self.module_map[node.module].items():
#            if method_key == 'id':
#                if node.module not in self._imports:
#                    self.write(f'require "{method_value}"')
#                    self._imports.append(node.module)
#
#        for method_key, method_value in self.module_map[node.module].items():
#            if method_value is None:
#                continue
#            if method_key == 'id':
#                continue
#
#            if method_key == 'mod_name':
#                self.write("include %s" % method_value)
#            else: # method_key == 'methods_map', etc..
#                for key, value in method_value.items(): # method_value: {'array':, 'prod': .. }
#                    if type(RB.__dict__[method_key]) != dict:
#                        continue
#                    if key not in RB.__dict__[method_key].keys():
#                        RB.__dict__[method_key][key] = value
#                    if isinstance(RB.__dict__[method_key][key], dict):
#                        if node.names[0].name == '*':
#                            RB.__dict__[method_key][key]['mod'] = ''
#                        elif node.names[0].name == key:
#                            RB.__dict__[method_key][key]['mod'] = ''
#                        else:
#                            RB.__dict__[method_key][key]['mod'] = _mod_name + '::'

    def _visit_Exec(self, node):
        pass

    def visit_Global(self, node):
        """
        Global(identifier* names)
        """
        #return self.visit(node.names.upper)
        self._scope.extend(node.names)

    def visit_Expr(self, node) -> None:
        """
        Expr(expr value)
        """
        val =  self.visit(node.value)
        if isinstance(node.value, ast.Str):
            #<Python>    """ * comment
            #                   * sub comment """
            #<Crystal>   # * comment
            #            #     * sub comment
            comment = val[1:-1]
            indent = self.indent_string()
            for s in comment.split('\n'):
                s = re.sub(r'^%s' % indent, '', s)
                self.write("# %s" % s)
        else:
            self.write(val)

    def visit_Pass(self, _node) -> None:
        self.write("# pass")

    def visit_Break(self, _node) -> None:
        self.write("break")

    def visit_Continue(self, _node) -> None:
        self.write("next")

    # Python 3
    def visit_arg(self, node):
        """
        (identifier arg, expr? annotation)
           attributes (int lineno, int col_offset)
        """
        return node.arg

    def visit_arguments(self, node) -> str:
        """
        <Python> (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults, arg? kwarg, expr* defaults)
        """
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        if node.vararg:
            args.append("*%s" % self.visit(node.vararg))
        return ", ".join(args)

    def visit_GeneratorExp(self, node):
        """
        GeneratorExp(expr elt, comprehension* generators)
        """
        #if isinstance(node.generators[0].iter, (ast.Tuple, ast.List)):
        #    i = "[%s]" % self.visit(node.generators[0].iter)
        #else:
        #    i = self.visit(node.generators[0].iter)
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        t = self.visit(node.generators[0].target)
        # <Python>    [x**2 for x in [1,2]]
        # <Crystal>   [1, 2].map{|x| x**2}
        return "%s.map{|%s| %s}" % (i, t, self.visit(node.elt))

    def visit_ListComp(self, node) -> str:
        """
        ListComp(expr elt, comprehension* generators)
        """
        #if isinstance(node.generators[0].iter, (ast.Tuple, ast.List)):
        #    i = "[%s]" % self.visit(node.generators[0].iter)
        #else:
        #    i = self.visit(node.generators[0].iter)
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        if isinstance(node.generators[0].target, ast.Name):
            t = self.visit(node.generators[0].target)
        else:
            # ast.Tuple
            # Goofy, but we need to wrap the returned values with ()
            # so that |a,b,c| ==> |(a,b,c)|
            self._tuple_type = '()'
            t = self.visit(node.generators[0].target)
            self._tuple_type = '[]'
        if len(node.generators[0].ifs) == 0:
            # <Python>    [x**2 for x in [1,2]]
            # <Crystal>   [1, 2].map{|x| x**2}
            return "%s.map{|%s| %s}" % (i, t, self.visit(node.elt))
        else:
            # <Python>    [x**2 for x in [1,2] if x > 1]
            # <Crystal>   [1, 2].select {|x| x > 1 }.map{|x| x**2}
            return "%s.select{|%s| %s}.map{|%s| %s}" % \
                    (i, t, self.visit(node.generators[0].ifs[0]), t, \
                     self.visit(node.elt))

    def visit_DictComp(self, node) -> str:
        """
        DictComp(expr key, expr value, comprehension* generators)
        """
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        if isinstance(node.generators[0].target, ast.Name):
            t = self.visit(node.generators[0].target)
        else:
            # ast.Tuple
            self._tuple_type = ''
            t = self.visit(node.generators[0].target)
            self._tuple_type = '[]'
        if len(node.generators[0].ifs) == 0:
            # <Python>    {key: data for key, data in {'a': 7}.items()}
            # <Crystal>   {'a', 7}.to_a.map{|key, data| [key, data]}.to_h
            return "%s.map{|%s|[%s, %s]}.to_h" % (i, t, self.visit(node.key), self.visit(node.value))
        else:
            # <Python> {key: data for key, data in {'a': 7}.items() if data > 6}
            # <Crystal>   {'a', 7}.to_a.select{|key, data| data > 6}.map{|key, data| [key, data]}.to_h
            return "%s.select{|%s| %s}.map{|%s|[%s, %s]}.to_h" % \
                    (i, t, self.visit(node.generators[0].ifs[0]), t, \
                     self.visit(node.key), self.visit(node.value))

    def visit_SetComp(self, node) -> str:
        """
        SetComp(expr elt, comprehension* generators)
        """
        i = self.visit(node.generators[0].iter) # ast.Tuple, ast.List, ast.*
        if isinstance(node.generators[0].target, ast.Name):
            t = self.visit(node.generators[0].target)
        else:
            # ast.Tuple
            self._tuple_type = ''
            t = self.visit(node.generators[0].target)
            self._tuple_type = '[]'
        if len(node.generators[0].ifs) == 0:
            # <Python> [x**2 for x in {1,2}]
            # <Crystal>   [1, 2].map{|x| x**2}.to_set
            return "%s.map{|%s| %s}.to_set" % (i, t, self.visit(node.elt))
        else:
            # <Python> [x**2 for x in {1,2} if x > 1]
            # <Crystal>   {1, 2}.select {|x| x > 1 }.map{|x| x**2}.to_set
            return "%s.select{|%s| %s}.map{|%s| %s}.to_set" % \
                    (i, t, self.visit(node.generators[0].ifs[0]), t, \
                     self.visit(node.elt))

    def visit_Lambda(self, node, style="normal") -> str:
        """
        Lambda(arguments args, expr body)
        """
        # [Lambda Definition] :
        #<Python>    lambda x,y :x*y
        #<Crystal>   ->(x,y) {x*y}
        #
        #<Python>    lambda *x: print(x)
        #<Crystal>   ->(*x) { print(x)}
        #
        #<Python>    def foo(x, y):
        #                x(y)
        #            foo(lambda x: print(a), a)
        #<Crystal>   def foo(x, y)
        #                x.(y)
        #            end
        #            foo(-> {|x| print(a)}, a)
        if style == "block":
            return "{ |%s| %s }" % (self.visit(node.args), self.visit(node.body))
        else:
            return "->(%s) { %s }" % (self.visit(node.args), self.visit(node.body))

    def visit_BoolOp(self, node) -> str:
        return (" %s " % self.get_bool_op(node)).join([ "%s" % self.ope_filter(self.visit(val)) for val in node.values ])

    def visit_UnaryOp(self, node) -> str:
        oper = self.get_unary_op(node)
        operand = self.visit(node.operand)
        # If we use a unary op on a simple item (constant/name), then just
        # use the unary op directly.  Otherwise put parenthesis around it
        simple_operand = isinstance(node.operand, (ast.Constant, ast.Name))
        if simple_operand:
            return "%s%s" % (oper, operand)
        else:
            return "%s(%s)" % (oper, operand)

    def visit_BinOp(self, node) -> str:
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Str):
            left = self.visit(node.left)
            # 'b=%(b)0d and c=%(c)d and d=%(d)d' => 'b=%<b>0d and c=%<c>d and d=%<d>d'
            left = re.sub(r"(.+?%)\((.+?)\)(.+?)", r"\1<\2>\3", left)
            self._dict_format = True
            right = self.visit(node.right)
            self._dict_format = False
            return f"{left} % {right}"
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Pow):
            return "%s ** %s" % (left, right)
        if isinstance(node.op, ast.Div):
            if re.search(r"Numo::", left) or re.search(r"Numo::", right):
                return "%s / %s" % (self.ope_filter(left), self.ope_filter(right))
            else:
                return "%s / %s.to_f" % (self.ope_filter(left), self.ope_filter(right))

        return "%s %s %s" % (self.ope_filter(left), self.get_binary_op(node), self.ope_filter(right))

    @scope
    def visit_Compare(self, node) -> str:
        """
        Compare(expr left, cmpop* ops, expr* comparators)
        """
        assert len(node.ops) == len(node.comparators)

        def compare_pair(left : str, comp : str, op):
            if (left == '__name__') and (comp == '"__main__"') or \
               (left == '"__main__"') and (comp == '__name__'):
                # <Python>     __name__ == '__main__':
                # <Crystal>    __FILE__ == PROGRAM_NAME
                left = '__FILE__'
                comp = 'PROGRAM_NAME'
            # Cannot necessarily use includes?, as includes? is not
            # defined for Hashes in Crystal, so chose to define a py_in?
            # method on String/Array/Hash
            if isinstance(op, ast.In):
                return "%s.py_in?(%s)" % (comp, left)
            elif isinstance(op, ast.NotIn):
                return "!%s.py_in?(%s)" % (comp, left)
            elif isinstance(op, ast.Eq):
                return "%s == %s" % (left, comp)
            elif isinstance(op, ast.NotEq):
                return "%s != %s" % (left, comp)
            elif isinstance(op, ast.IsNot):
                return "!%s.equal?(%s)" % (left, comp)
            else:
                return "%s %s %s" % (left, self.get_comparison_op(op), comp)

        # This handles python's `a < b < c` to convert to `(a < b) && (b < c)`
        compare_list : List[str] = []
        comp : str = "???" # fake initial value
        for i in range(len(node.ops)):
            if i == 0:
                left = self.visit(node.left)
            else:
                left = comp
            comp = self.visit(node.comparators[i])
            op = node.ops[i]
            pair = compare_pair(left, comp, op)
            if len(node.ops) == 1:
                return pair
            compare_list.append('(' + pair + ')')
        return ' && '.join(compare_list)

    # python 3
    def visit_Starred(self, node) -> str:
        """
        Starred(expr value, expr_context ctx)
        """
        return "*" + self.visit(node.value)

    # python 3
    def visit_NameConstant(self, node) -> str:
        """
        NameConstant(singleton value)
        """
        value = node.value
        value = self.name_constant_map[value]
        return value

    def visit_Name(self, node) -> str:
        """
        Name(identifier id, expr_context ctx)
        """
        nid = node.id

        try:
            if self._call:
                nid = self.func_name_map[nid]
            else:
                # TODO: for cases where we import attributes
                # from modules, we would need to perform
                # some sort of lookup.  E.g. if we do:
                #   from numpy import ndarray
                # ... or:
                #   from numpy import *
                # ... then we need to be able to evaluate:
                #   isinstance(foo, ndarray)
                if nid in self.methods_map.keys():

                    rtn = self.get_methods_map(self.methods_map[nid])
                    if rtn != '':
                        nid = rtn
                else:
                    nid = self.name_map[nid]
        except KeyError:
            pass

        try:
            nid = self.exception_map[nid]
        except KeyError:
            pass

        return nid

    def visit_Num(self, node) -> str:
        return str(node.n)

    # Python 3
    def visit_Bytes(self, node):
        """
        Bytes(bytes s)
        """
        # Likely doesn't work at all.
        # Unsure how to handle in Crystal at this time...
        return node.s

    # Python 3
    def visit_Ellipsis(self, _node):
        """
        Ellipsis
        """
        return 'false'


    # Python 3.8+ uses ast.Constant instead of ast.NamedConstant
    def visit_Constant(self, node) -> str:
        value = node.value

        if value is True or value is False or value is None:
            return self.name_constant_map[value]
        elif isinstance(value, str):
            return self.visit_Str(node)
        elif isinstance(value, bytes):
            return self.visit_Bytes(node)
        elif node.value == Ellipsis:
            return self.visit_Ellipsis(node)
        else:
            # need to handle complex()
            # >>> print(type(node.value))
            return repr(node.s)

    def visit_Str(self, node) -> str:
        """
        Str(string s)
        """
        # Uses the Python builtin repr() of a string and the strip string type from it.
        txt = re.sub(r'"', '\\"', repr(node.s)[1:-1])
        txt = re.sub(r'\\n', '\n', txt)
        txt = re.sub(r'#([$@{])', r'\#\1', txt)
        if self._is_string_symbol:
            txt = ':' + txt
        else:
            txt = '"' + txt + '"'
        return txt

    def visit_JoinedStr(self, node) -> str:
        txt = ""
        for val in node.values:
            if self.name(val) == "FormattedValue":
                txt = txt + "#{" + self.visit(val) + "}"
            else:
                txt = txt + self.visit(val)[1:-1]
        return '"' + txt + '"'

    def visit_FormattedValue(self, node) -> str:
        conversion = node.conversion
        if conversion == 97:
            # ascii
            raise NotImplementedError("Cannot handle {!a} f-string conversions yet")
        elif conversion == 114:
            # repr
            return self.visit(node.value) + ".inspect"
        elif conversion == 115:
            # string
            return self.visit(node.value) + ".to_s"
        else:
            return self.visit(node.value)

    def key_list_check(self, key_list, rb_args):
        j = 0
        star = 0
        wstar = 0

        star_i = False
        wstar_i = False
        for i in range(len(key_list)):
            if '**' in key_list[i]:
                star_i = i
            elif '*' in key_list[i]:
                wstar_i = i

        key_l = []
        for i in range(len(key_list)):
            self.vprint("key_list_check j:%s i:%s rb_args: %s key_list %s" % (j, i, rb_args, key_list))

            if len(rb_args) <= j:
                break

            if '**' in key_list[i]:
                rb_args_j = rb_args[j:]
                for rb_arg in rb_args_j:
                    if ': ' in rb_arg:
                        j += 1
                        wstar=1
            elif '*' in key_list[i]:
                rb_args_j = rb_args[j:]
                for rb_arg in rb_args_j:
                    if ': ' in rb_arg:
                        break
                    else:
                        j += 1
                        star=1
            else:
                j += 1
        if len(rb_args) != j:
            return False

        key_l = key_list[:]
        if wstar_i is not False:
            if wstar != 1:
                key_l = key_l[:-1]
        if star_i is not False:
            if star != 1:
                key_l = key_l[:-1]

        return key_l

    def get_key_list(self, rb_args, key_lists):
        if rb_args is False:
            return False
        #key: - ['stop']                           : len(rb_args) == 1
        #____ - ['start', 'stop', 'step', 'dtype'] : len(rb_args) != 1
        for key_list in key_lists:
            l = self.key_list_check(key_list, rb_args)
            self.vprint("get_key_list len(key_list): %s l: %s" % (len(key_list), l))
            if l is not False:
                self.vprint("get_key_list %s" % l)
                return l
        return False

    # method_map : self.methods_map[func] # e.g. numpy[methods_map][prod]
    def get_methods_map(self, method_map, rb_args=False, ins=False):
        """
        [Function convert to Method]
        <Python> np.prod(shape, axis=1, keepdims=True)
        <Crystal>   Numo::NArray[shape].prod(axis:1, keepdims:true)
        """
        if rb_args is False:
            if 'key' in method_map.keys():
                return ''

        key_list = False
        key_order_list = False
        if rb_args is not False:
            if 'key' in method_map.keys():
                key_list = self.get_key_list(rb_args, method_map['key'])
            if 'key_order' in method_map.keys():
                key_order_list = self.get_key_list(rb_args, method_map['key_order'])

        rtn = False
        if key_list is not False:
            if 'rtn_star' in method_map.keys():
                for i in range(len(method_map['rtn_star'])):
                    if len(key_list) == i:
                        rtn = method_map['rtn_star'][i]
                        break
                else:
                    rtn = method_map['rtn_star'][-1]
        if (rtn is False) and (rb_args is not False):
            if 'rtn' in method_map.keys():
                for i in range(len(method_map['rtn'])):
                    if len(rb_args) == i:
                        rtn = method_map['rtn'][i]
                        break
                else:
                    rtn = method_map['rtn'][-1]

        mod = ''
        if 'mod' in method_map.keys():
            mod = method_map['mod']

        bracket = True
        if 'bracket' in method_map.keys():
            if method_map['bracket'] is False:
                bracket = False
        main_data = ''
        main_func = ''
        m_args = []
        args_hash = {}
        if key_list:
            for i in range(len(key_list)):
                key = key_list[i]
                if '**' in key:
                    args_hash[key] = []
                elif '*' in key:
                    args_hash[key] = []
        func_key = method_map.get('main_func_key', '')  # dtype
        if rb_args and (key_list is not False):
            i = 0
            for j in range(len(rb_args)):
                if '**' in key_list[i]:
                    if ': ' in rb_args[j]:
                        key = key_list[i]
                        value = rb_args[j]
                        args_hash[key].append(value)
                elif '*' in key_list[i]:
                    key = key_list[i]
                    value = rb_args[j]
                    args_hash[key].append(value)
                    if (len(key_list) > i) and (len(rb_args) > j + 1):
                        if ': ' in rb_args[j+1]:
                            i += 1
                else:
                    if ': ' in rb_args[j]:
                        key, value = rb_args[j].split(': ', 1)
                    else:
                        key = key_list[i]
                        value = rb_args[j]
                    args_hash[key] = value
                    i += 1
            self.vprint("get_methods_map func_key : %s : args_hash %s" % (func_key, args_hash))
            if key_order_list is not False:
                key_list = key_order_list
            for key in key_list:
                if key == func_key:
                    continue
                if key not in args_hash:
                    continue
                value = args_hash[key]
                if key in method_map['val'].keys():
                    if method_map['val'][key] is True:
                        if isinstance(value, list):
                            value = ', '.join(value)
                        m_args.append(value)
                        args_hash[key] = value
                    elif isinstance(method_map['val'][key], str):
                        if "%" in method_map['val'][key]:
                            m_args.append(method_map['val'][key] % {key: value})
                            args_hash[key] = method_map['val'][key] % {key: value}
                        else:
                            m_args.append("%s: %s" % (key, value))
                            args_hash[key] = value
                    elif method_map['val'][key] is False:
                        continue
                    elif self._verbose:
                        print("get_methods_map key : %s not match method_map['val'][key] %s" % (key, method_map['val'][key]))
            if len(args_hash) == 0:
                self.set_result(ResultStatus.INCLUDE_ERROR)
                raise CrystalError("methods_map default argument Error : not found args")

            if 'main_data_key' in method_map:
                data_key = method_map['main_data_key']
                if not data_key in args_hash:
                    raise Exception("Error: Missing key '%s' from args_hash" % data_key)
                main_data = args_hash[data_key]

        if 'main_func' in method_map.keys():
            main_func = method_map['main_func'] % {'mod': mod, 'data': main_data}
        else:
            for kw, val in args_hash.items():
                if kw in method_map['val'].keys() and kw == func_key:
                    for key in method_map['main_func_hash'].keys():
                        # [Function convert to Method]
                        # <Python>   dtype=np.int32
                        # <Crystal>   Numo::Int32
                        if "%s" in key:
                            key2 = (key % ins) # key2: np.int32
                        if val == key2:
                            main_func = method_map['main_func_hash'][key]
            else:
                if main_func == '' and 'main_func_hash_nm' in method_map.keys():
                    main_func = method_map['main_func_hash_nm']
            main_func = method_map['val'][func_key] % {'mod': mod, 'data': main_data, 'main_func': main_func}
        if main_func == '':
            self.set_result(ResultStatus.INCLUDE_ERROR)
            raise CrystalError("methods_map main function Error : not found args")

        if rtn:
            self.vprint("get_methods_map main_func : %s : rtn %s" % (main_func, rtn))
            rtn = rtn % args_hash
            self.vprint("get_methods_map main_func : %s : rtn %s" % (main_func, rtn))
            return "%s%s" % (main_func, rtn)

        if bracket:
            self.vprint("get_methods_map with bracket main_func : %s : m_args %s" % (main_func, m_args))
            return "%s(%s)" % (main_func, ', '.join(m_args))
        else:
            self.vprint("get_methods_map without bracket main_func : %s : m_args %s" % (main_func, m_args))
            return "%s%s" % (main_func, ', '.join(m_args))

    def visit_keyword(self, node):
        """ 
        Keyword in a function call
        <Python> run_func(kw="value")
        <Crystal run_func(kw: "value")
        """
        keyname = node.arg
        kwvalue = self.visit(node.value)
        return f"{keyname}: {kwvalue}"

    def visit_Call(self, node, crytype = None):
        """
        Call(expr func, expr* args, keyword* keywords)
        """
        funcdb = FuncCall(cryvisit=self, node=node, crytype=crytype)
        cry_args = funcdb.crystal_args

        # [method argument set Method Object] :
        # <Python>    def describe():
        #                 return "world"
        #             describe = mydecorator(describe)
        #
        # <Crystal>   def describe()
        #                 return "world"
        #             end
        #             describe = mydecorator(method(:describe))
        self._func_args_len = len(cry_args)
        if not isinstance(node.func, ast.Call):
            self._call = True
        func = self.visit(node.func)
        self.vprint("Call func_name[%s]" % func)
        if not isinstance(node.func, ast.Call):
            self._call = False

        # [Inherited Instance Method]
        opt = None
        if self._class_name:
            for base_class in self._classes_base_classes[self._class_name]:
                base_func = "%s.%s" % (base_class, func)
                if base_func in self.methods_map.keys():
                    if 'option' in self.methods_map[base_func].keys():
                        opt = self.methods_map[base_func]['option']
                        self.vprint("Call option: %s : %s" % (func, opt))

        for f in self._import_files:
            self.vprint("Call func: %s : f %s" % (func, f))
            if func.startswith(f):
                self.vprint("Call func: %s " % func)
                func = func.replace(f + '.', '', 1)
                # <Python>    imported.moduleb.moduleb_class
                # <Crystal>   Imported::Moduleb::Moduleb_class (base_path_count=0)
                #                       Moduleb::Moduleb_class (base_path_count=1)
                if func in self._class_names:
                    func = formatter.capitalize(func) + '.new'
                # <Python>    * tests/modules/imported/modulec.py
                #               import imported.submodules.submodulea
                #               imported.submodules.submodulea.foo()
                # <Crystal>   * tests/modules/imported/modulec.cr
                #               require_relative "submodules/submodulea"
                #               Submodules::Submodulea::foo()
                base = '::'.join([formatter.capitalize(x) for x in f.split('.')[self._base_path_count:]])
                if base != '':
                    func = base + '.' + func # was '::'
                self.vprint("Call func: %s" % func)
                break

            f = '.'.join(f.split('.')[self._base_path_count:])
            x = [x for x in self._rel_path if x.startswith(f + '.')]
            if len(x) != 0:
                f = x[0].replace(f + '.', '')

            if func.startswith(f):
                self.vprint("Call mod_paths : func : %s " % func)
                func = func.replace(f + '.', '')
                if func in self._class_names:
                    func = formatter.capitalize(func) + '.new'
                # <Python>    * tests/modules/imported/modulee.py
                #               from imported.submodules import submodulea
                #               submodulea.foo()
                # <Crystal>   * tests/modules/imported/modulee.cr
                #               require_relative 'submodules/submodulea'
                #               include Submodules
                #               Submodulea::foo()
                base = '::'.join([formatter.capitalize(x) for x in f.split('.')])
                if base != '':
                    func = base + '::' + func
                self.vprint("Call func: %s" % func)
                break

        # [Class Instance Create] :
        # <Python>    foo()
        # <Crystal>   Foo.new()

        if func in self._class_names:
            func = formatter.capitalize(func) + '.new'


        # At this point, we have massaged the func.variable enough...
        # now attach it to the funcdb
        funcdb.set_func(func)

        # [method argument set Keyword Variables] :
        # <Python>    def foo(a, b=3): <...>
        #             foo(a, 5)
        # <Crystal>   def foo (a, b: 3) <...>
        #             foo(a, b:5)
        func_arg = None
        is_static = False
        if func.find('.') == -1:
            if (func in self._functions) and \
               (not ([None] in self._functions[func])):
                func_arg = self._functions[func]
            ins = ''
        else:
            ins, method = func.split('.', 1)
            if (method in self._class_functions):
                is_static = True
            if (ins in self._classes_class_functions_args) and \
               (method in self._classes_class_functions_args[ins]) and \
               (not ([None] in self._classes_class_functions_args[ins][method])):
                func_arg = self._classes_class_functions_args[ins][method]
            if (ins in self._classes_self_functions_args) and \
               (method in self._classes_self_functions_args[ins]) and \
               (not ([None] in self._classes_self_functions_args[ins][method])):
                func_arg = self._classes_self_functions_args[ins][method]

        if func in self.methods_map_middle.keys():
            # [Function convert to Method]
            #<Python>    isinstance(foo, String)
            #<Crystal>   foo.is_a? String
            if len(cry_args) == 1:
                return "%s.%s" % (cry_args[0], self.methods_map_middle[func])
            else:
                return "%s.%s %s" % (cry_args[0], self.methods_map_middle[func], cry_args[1])

        if is_static is False:
            if ((len(cry_args) != 0 ) and (cry_args[0] == 'self')):
                del cry_args[0]
                self._func_args_len = len(cry_args)

        # Use keyword argments in function defined case.
        if func_arg is not None:
            if ((len(cry_args) != 0 ) and (cry_args[0] == 'self')):
                args = cry_args[1:]
            else:
                args = cry_args
            for i in range(len(args)):
                #print("i[%s]:%s" % (i, args[i]))
                if len(func_arg) <= i:
                    break
                if (func_arg[i] is not None) and (func_arg[i] != []):
                    cry_args[i] = "%s: %s" % (func_arg[i], cry_args[i])

        self._func_args_len = 0

        #cry_args = []
        #for arg in node.args:
        #    if isinstance(arg, (ast.Tuple, ast.List)):
        #       cry_args.append("[%s]" % self.visit(arg))
        #    else:
        #       cry_args.append(self.visit(arg))
        # ast.Tuple, ast.List, ast.*
        cry_args_base = copy.deepcopy(cry_args)
        if node.keywords:
            # [Keyword Argument] :
            # <Python>    foo(1, fuga=2):
            # <Crystal>   foo(1, fuga: 2)
            for kw in node.keywords:
                cry_args.append(self.visit(kw))
                self._conv = False
                cry_args_base.append(self.visit(kw))
                self._conv = True
        if len(cry_args) == 0:
            cry_args_s = ''
        elif len(cry_args) == 1:
            cry_args_s = cry_args[0]
        elif hasattr(cry_args[0], "decode"):
            cry_args_s = b", ".join(cry_args)
        else:
            cry_args_s = ", ".join(cry_args)

        if isinstance(node.func, ast.Call):
            return f"{func}.py_call({cry_args_s})"


        func_modulename = funcdb.func_module

        # de-alias the modulename to look it up for translation
        dealias_modulename = self._module_aliases.get(func_modulename, func_modulename)
        self.vprint(f"looking up: module({func_modulename}=>{dealias_modulename}) func=({funcdb.func_name})")


        lkfunc = registry.func_lookup(dealias_modulename, funcdb.func_name)
        if lkfunc:
            return lkfunc(funcdb)

        if func in self.ignore.keys():
            # [Function convert to Method]
            # <Python>    unittest.main()
            # <Crystal>   ""
            return ""
        elif func in self.minmax_like_methods.keys():
            # [Function convert to Method (special min-max case)]
            # This is a special case b/c pythons min/max can take
            # either one iterable arg (list/tuple) or
            # multiple scalar values which we will interpret as a tuple
            # <Py2cr.1>    max(foo,bar,baz) => {foo,bar,baz}.max
            # <Py2cr.2>    max([foo,bar,baz]) => [foo,bar,baz].max
            # <Py2cr.3>    max((foo,bar,baz)) => {foo,bar,baz}.max
            if len(cry_args) > 1: # multiple scalars
                return "{%s}.%s" % (self.ope_filter(cry_args_s), func)
            else:
                return "%s.%s" % (self.ope_filter(cry_args_s), func)


        elif func in self.reverse_methods.keys():
            # [Function convert to Method]
            # <Python>    float(foo)
            # <Crystal>   (foo).to_f
            cry_func = self.reverse_methods[func]
            #if not isinstance(self.reverse_methods[func], dict):
            if len(cry_args) == 1:
                return "%s.%s" % (self.ope_filter(cry_args_s), cry_func)
            else:
                return "%s.%s(%s)" % (self.ope_filter(cry_args[0]), cry_func,
                                      ", ".join(cry_args[1:]))

            #--------------------------------------
            # Next part used to go with yaml-function-defs which
            # we dont have anymore... however it may be useful with some
            # functions like: `round(a,b)`
            #--------------------------------------
            #if len(cry_args) == 1:
            #    if 'arg_count_1' in self.reverse_methods[func].keys():
            #        return "%s.%s" % (self.ope_filter(cry_args_s), self.reverse_methods[func]['arg_count_1'])
            #else:
            #    if 'arg_count_2' in self.reverse_methods[func].keys():
            #        return "%s.%s(%s)" % (self.ope_filter(cry_args[0]), self.reverse_methods[func]['arg_count_2'], ", ".join(cry_args[1:]))



        elif func in self.methods_map.keys():
            return self.get_methods_map(self.methods_map[func], cry_args_base, ins)
        elif func in self.order_methods_with_bracket.keys():
            # [Function convert to Method]
            # <Python>    os.path.dirname(name)
            # <Crystal>   File.dirname(name)
            return "%s(%s)" % (self.order_methods_with_bracket[func], ','.join(cry_args))
        elif isinstance(node.func, ast.Attribute) and (node.func.attr in self.call_attribute_map):
            # [?? convert to Method]
            # <Python>    ' '.join(['a', 'b'])
            # <Crystal>   ['a', 'b'].join(' ')
            return "%s.%s" % (cry_args_s, func)
        elif isinstance(node.func, ast.Lambda) or (func in self._lambda_functions):
            # [Lambda Call] :
            # <Python>    (lambda x:x*x)(4)
            # <Crystal>   lambda{|x| x*x}.call(4)
            # <Python>    foo = lambda x:x*x
            #             foo(4)
            # <Crystal>   foo = lambda{|x| x*x}
            #             foo.call(4)
            return "%s.call(%s)" % (func, cry_args_s)
        elif self._class_name:
            # [Inherited Instance Method]
            self.vprint("self._classes_base_classes : %s" % self._classes_base_classes[self._class_name])
            for base_class in self._classes_base_classes[self._class_name]:
                base_func = "%s.%s" % (base_class, func)
                self.vprint("base_func : %s" % base_func)
                if base_func in self.methods_map.keys():
                    self.vprint("Call Inherited Instance Method : %s : base_func %s" % (base_func, cry_args))
                    return self.get_methods_map(self.methods_map[base_func], cry_args, ins)
                if base_func in self.order_methods_with_bracket.keys():
                    # [Inherited Instance Method] :
                    # <Python>    self.assertEqual()
                    # <Crystal>   assert_equal()
                    return "%s(%s)" % (self.order_methods_with_bracket[base_func], ','.join(cry_args))

        if (func in self._scope or func[0] == '@') and \
           func.find('.') == -1: # Proc call
            return "%s.py_call(%s)" % (func, cry_args_s)

        if func[-1] == ')':
            return func
        else:
            return f"{func}({cry_args_s})"

    def visit_Raise(self, node) -> None:
        """
        Raise(expr? exc, expr? cause)
        """
        if node.exc is None:
            self.write("raise Exception.new()")
        elif isinstance(node.exc, ast.Name):
            self.write("raise %s" % self.visit(node.exc))
        elif isinstance(node.exc, ast.Call):
            if len(node.exc.args) == 0:
                self.write("raise %s" % self.visit(node.exc))
            else:
                # [Exception] :
                # <Python>    raise ValueError('foo.')
                # <Crystal>   raise TypeError.new("foo.")
                self.write("raise %s.new(%s)" % (self.visit(node.exc.func), self.visit(node.exc.args[0])))


    def visit_Attribute(self, node) -> str:
        """
        Attribute(expr value, identifier attr, expr_context ctx)
        """
        attr = node.attr

        if (attr != '') and isinstance(node.value, ast.Name) and (node.value.id != 'self'):
            # get modulename for this attr if it exists, and if it does,
            # then de-alias it (e.g. np.xyz -> numpy.xyz)
            rawattr_modname = self.visit(node.value)
            attr_modname = self._module_aliases.get(rawattr_modname,rawattr_modname)
            mod_attr = "%s.%s" % (attr_modname, attr)
        else:
            attr_modname = ''
            mod_attr = ''

        self.vprint(f"Attribute attr_name[{attr}] mod={attr_modname} mod_attr={mod_attr}")

        if not (isinstance(node.value, ast.Name) and (node.value.id == 'self')):
            renamed_attr = registry.attr_lookup(attr_modname, attr)

            # Pre-map the attributes (e.g write => print)
            if attr in self.attribute_map.keys():
                # [Attribute method converter]
                # <Python>    fuga.append(bar)
                # <Crystal>   fuga.push(bar)
                attr = self.attribute_map[attr]

            if renamed_attr:
                return renamed_attr

#            if mod_attr in self.attribute_map.keys():
#                """ [Attribute method converter]
#                <Python> six.PY3 # True
#                <Crystal>   true   """
#                return self.attribute_map[mod_attr]
            if self._conv and (attr in self.methods_map.keys()):
                rtn = self.get_methods_map(self.methods_map[attr])
                if rtn != '':
                    return rtn
            if self._conv and (mod_attr in self.methods_map.keys()):
                rtn =  self.get_methods_map(self.methods_map[mod_attr])
                if rtn != '':
                    return rtn
            if self._func_args_len == 0:
                # [Attribute method converter without args]
                # <Python>     fuga.split()
                # <Crystal>   fuga.split()
                if attr in self.attribute_not_arg.keys():
                    attr = self.attribute_not_arg[attr]
            else:
                # [Attribute method converter with args]
                # <Python>    fuga.split(foo,bar)
                # <Crystal>   fuga.split_p(foo,bar)
                if attr in self.attribute_with_arg.keys():
                    attr = self.attribute_with_arg[attr]

        if isinstance(node.value, ast.Call):
            # [Inherited Class method call]
            #<Python> class bar(object):
            #             def __init__(self,name):
            #                 self.name = name
            #         class foo(bar):
            #             def __init__(self,val,name):
            #                 super(bar, self).__init__(name)
            #
            #<Crystal>   class Bar
            #               def initialize(name)
            #                   @name = name
            #               end
            #            end
            #            class Foo < Bar
            #               def initialize(val, name)
            #                   super(name)
            #               end
            #            end
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id == 'super':
                    if attr == self._function[-1]:
                        return "super"
                    elif attr in self._self_functions:
                        return "public_method(:%s).super_method.call" % attr
                    else:
                        return attr
        elif isinstance(node.value, ast.Name):
            if node.value.id == 'self':
                if attr in self._class_functions:
                    # [Class Method] :
                    # <Python>    self.bar()
                    # <Crystal>   Foo.bar()
                    return "%s.%s" % (self._rclass_name, attr)
                elif attr in self._self_functions:
                    # [Instance Method] :
                    # <Python>    self.bar()
                    # <Crystal>   bar()
                    return attr
                elif self._class_name:
                    for base_class in self._classes_base_classes[self._class_name]:
                        func = "%s.%s" % (base_class, attr)
                        # [Inherited Instance Method] :
                        # <Python>    self.(assert)
                        # <Crystal>   assert()
                        if func in self.methods_map.keys():
                            return attr
                        if func in self.order_methods_with_bracket.keys():
                            return attr
                        if (base_class in self._classes_self_functions) and \
                           (attr in self._classes_self_functions[base_class]):
                            # [Inherited Instance Method] :
                            # <Python> self.bar()
                            # <Crystal>   bar()
                            return attr
                    else:
                        # [Instance Variable] :
                        # <Python> self.bar
                        # <Crystal>   @bar
                        self._class_self_variables.append(attr)
                        return "@%s" % (attr)
            elif self._class_name and (node.value.id in self._classes_base_classes[self._class_name]):
                # [Inherited Class method call]
                #<Python> class bar(object):
                #             def __init__(self,name):
                #                 self.name = name
                #         class foo(bar):
                #             def __init__(self,val,name):
                #                 bar.__init__(self,name)
                #
                #<Crystal>   class Bar
                #             def initialize(name)
                #                 @name = name
                #             end
                #         end
                #         class Foo < Bar
                #             def initialize(val, name)
                #                 super(name)
                #             end
                #         end
                if attr == self._function[-1]:
                    return "super"
                elif attr in self._self_functions:
                    return "public_method(:%s).super_method.call" % attr
                else:
                    return attr

            elif node.value.id == self._class_name:
                if attr in self._class_variables:
                    # [class variable] :
                    # <Python>    foo.bar
                    # <Crystal>   @@bar
                    return f"@@{attr}"
            elif node.value.id in self._class_names:
                if attr in self._classes_functions[node.value.id]:
                    # [class variable] :
                    # <Python>    foo.bar
                    # <Crystal>   Foo.bar
                    return "%s.%s" % (node.value.id[0].upper() + node.value.id[1:], attr)
            #elif node.value.id in self.module_as_map:
            #    """ [module alias name] :
            #    <Python> np.array([1, 1])
            #    <Crystal>   Numo::NArray[1, 1]
            #    """
            #    if attr in self.module_as_map[node.value.id].keys():
            #        return "%s" % (self.module_as_map[node.value.id][attr])
            #    """ [module alias name] :
            #    <Python> np.sum(np.array([1,1]))
            #    <Crystal>   Numo::NArray[1, 1].sum
            #    """
        elif isinstance(node.value, ast.Str):
            if node.attr in self.call_attribute_map:
                # [attribute convert]
                #<Python>    ' '.join(ary)
                #<Crystal>   ary.join(' ')
                return "%s(%s)" % (attr, self.visit(node.value))
        v = self.visit(node.value)
        if attr != '':
            return "%s.%s" % (self.ope_filter(v), attr)
        else:
            return v

    @staticmethod
    def ope_filter(node_value : str) -> str:
        """Tweak stringified value to wrap in parenthesis if it looks mathematical"""
        if '-' in node_value:
            return '(' + node_value + ')'
        elif '+' in node_value:
            return '(' + node_value + ')'
        elif '*' in node_value:
            return '(' + node_value + ')'
        elif '/' in node_value:
            return '(' + node_value + ')'
        elif '%' in node_value:
            return '(' + node_value + ')'

        # not include operator
        return node_value

    def visit_Tuple(self, node) -> str:
        """
        Tuple(expr* elts, expr_context ctx)
        """
        els = [self.visit(e) for e in node.elts]
        if not els:
            return "Tuple.new"
        elif self._tuple_type == '()':
            return "(%s)" % (", ".join(els))
        elif self._tuple_type == '[]':
            return "{%s}" % (", ".join(els))
        elif self._tuple_type == '=>':
            return "%s => %s" % (els[0], els[1])
        elif self._tuple_type == '':
            return "%s" % (", ".join(els))
        else:
            self.set_result(ResultStatus.INCLUDE_ERROR)
            raise CrystalError("tuples in argument list Error")

    def visit_Dict(self, node, crytype = None) -> str:
        """
        Dict(expr* keys, expr* values)
        """
        els = []
        for k, v in zip(node.keys, node.values):
            keystr, valstr = self.visit(k), self.visit(v)
            if isinstance(k, ast.Name):
                els.append(f'"{keystr}" => {valstr}')
            elif self._dict_format is True: # ast.Str
                els.append(f"{keystr}: {valstr}")
            else: # ast.Str, ast.Num
                els.append(f"{keystr} => {valstr}")

        if els:
            return "{" + ", ".join(els) + "}"
        else:
            return self.empty_hash(node, crytype)


    def visit_List(self, node, crytype = None) -> str:
        """
	List(expr* elts, expr_context ctx)
        """
        els = [self.visit(e) for e in node.elts]
        if els:
            return "[%s]" % (", ".join(els))
        else:
            return self.empty_list(node, crytype)

    def visit_Set(self, node) -> str:
        els = [self.visit(e) for e in node.elts]
        return "Set.new([%s])" % (", ".join(els))

    def visit_ExtSlice(self, node) -> str:
        """
        ExtSlice(slice* dims)

        <Python>    np.asarray([[1,2,3],[4,5,6]])[0,:]
        <Crystal>   Numo::SFloat[[1,2,3],[4,5,6]][0, 0..-1]
        """
        s = []
        for e in node.dims:
            s.append(self.visit(e))
        return ", ".join(s)

    def process_slice_with_step(self, node) -> Tuple[str, Optional[str]]:
        """ 
        Special subcase of visit_Slice where we want to return
        a range-string plus a separate step-function that will be
        used to tack on after the Subscript
        """
        lowval = self.visit(node.lower) if node.lower else 0
        if node.upper:
            rngstr = "%s...%s" % (lowval, self.visit(node.upper))
        else:
            rngstr = "%s..-1" % lowval

        # suffix function to do stepping.
        # Unfortunately for crystal this returns an Array and not a Slice :(
        if node.step:
            suffix = "each_slice(%s).map(&.first)" % self.visit(node.step)
            return (rngstr, suffix)

        # no step, no suffix.
        return (rngstr, None)

    def visit_Slice(self, node) -> str:
        """
        Slice(expr? lower, expr? upper, expr? step)
        """
        rangestr, _ = self.process_slice_with_step(node)
        return rangestr

    def visit_Subscript(self, node) -> str:
        self._is_string_symbol = False
        name = self.visit(node.value)
        filtname = self.ope_filter(name)
        if isinstance(node.slice, (ast.Index, ast.Constant, ast.Name)):
            for arg in self._function_args:
                if arg == f"**{name}":
                    self._is_string_symbol = True
            index = self.visit(node.slice)
            self._is_string_symbol = False
            return "%s[%s]" % (filtname, index)
        if isinstance(node.slice, (ast.ExtSlice)):
            s = self.visit(node.slice)
            return "%s[%s]" % (filtname, s)
        elif isinstance(node.slice, (ast.Slice)):
            rangestr, suffix = self.process_slice_with_step(node.slice)
            if suffix:
                return "%s[%s].%s" % (filtname, rangestr, suffix)
            return "%s[%s]" % (filtname, rangestr)
        else:
            s = self.visit(node.slice)
            return "%s[%s]" % (filtname, s)


    def visit_Index(self, node : ast.Index) -> str:
        return self.visit(node.value)


    def visit_Yield(self, node : ast.Yield) -> str:
        """
        <Python>    def func():
                        yield 1
                    gen = func()
                    gen.__next__()
        <Crystal>   func = Fiber.new {
                      Fiber.yield 1
                    }
                    func.resume
        """
        if node.value:
            self.maybewarn("'yield %s' is not supported" % self.visit(node.value))
            return "yield(%s)" % (self.visit(node.value))
        else:
            self.maybewarn("'yield' is not supported")
            return "yield"

    def empty_list(self, node : ast.AST, crytype = None) -> str:
        """
        Return Crystal representation of an empty Array
        Crystal needs the annotation. If we dont have one on the
        Python side, then warn.
        """
        if crytype:
            anno = crytype.unwrap_list()
            return "[] of %s" % (anno)
        else:
            self.maybewarn("empty-list infer issue (%s line:%d col:%d)" % (node, node.lineno, node.col_offset))
            return "[]"

    def empty_hash(self, node : ast.AST, crytype = None) -> str:
        """
        Return Crystal representation of an empty Hash
        Crystal needs the annotation. If we dont have one on the
        Python side, then warn.
        """
        if crytype:
            annokey, annoval = crytype.unwrap_dict()
            return "{} of %s => %s" % (annokey, annoval)
        else:
            self.maybewarn("empty-dict infer issue (%s line:%d col:%d)" % (node, node.lineno, node.col_offset))
            return "{}"


def convert_py2cr(s : str, dir_path : str , path : str = '', base_path_count : int = 0, modules : List[str] = None, mod_paths : Dict[str, str] = None, no_stop : bool = False, verbose : bool = False):
    """
    Takes Python code as a string 's' and converts this to Crystal.

    Example:

    >>> convert_py2cr("x[3:]")
    'x[3..-1]'

    """
    modules = modules or []
    mod_paths = mod_paths or {}

    # get modules information
    visitor = RB(path, dir_path, base_path_count, mod_paths, verbose=verbose)
    visitor.mode(2)
    for m in modules:
        t = ast.parse(m)
        visitor.visit(t)
        visitor.clear() # clear self.__buffer

    # convert target file
    target_file = ast.parse(s)
    if no_stop:
        visitor.mode(1)
    else:
        visitor.mode(0)
    visitor.visit(target_file)

    data = visitor.read()
    visitor.clear() # clear self.__buffer

    header = visitor.read()

    return (visitor.get_result(), header, data)

def convert_py2cr_write(filename, base_path_count=0, subfilenames=None, base_path=None, require=None, output=None, force=None, no_stop=False, verbose=False):
    subfilenames = subfilenames or []

    if output:
        if not force:
            if os.path.exists(output):
                sys.stderr.write('Skip : %s already exists.\n' % output)
                return 3
        output = open(output, "w", encoding="utf-8")
    else:
        output = sys.stdout

    if require:
        output.write("require \"py2cr\"\n")

    mods = []
    mod_paths = OrderedDict()
    for sf in subfilenames:
        rel_path = os.path.relpath(sf, os.path.dirname(filename))
        name_path, _ext = os.path.splitext(rel_path)
        mod_paths[sf] = name_path
        with open(sf, 'r', encoding="utf-8") as f:
            mods.append(f.read()) #unsafe for large files!
    name_path = ''
    dir_path = ''
    if base_path:
        # filename  : tests/modules/classname.py
        # base_path : tests/modules
        dir_path = os.path.relpath(os.path.dirname(filename), base_path)
        if dir_path != '.':
            rel_path = os.path.relpath(filename, base_path)
            name_path, _ext = os.path.splitext(rel_path)
        else:
            dir_path = ''
    with open(filename, 'r', encoding="utf-8") as f:
        s = f.read() # unsafe for large files!
        rtn, header, data = convert_py2cr(s, dir_path, name_path, base_path_count, mods, mod_paths, no_stop=no_stop, verbose=verbose)
        if require:
            output.write(header)
        output.write(data)

    # close the filehandle if it isnt stdout.
    if output is not sys.stdout:
        output.close()
    return rtn

def main() -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options] filename.py\n" \
        + "    or %(prog)s [-w [-f]] [-(r|b)] [-v] filename.py\n" \
        + "    or %(prog)s -p foo/bar/ -m [-w [-f]] [-(r|b)] [-v] foo/bar/filename.py\n" \
        + "    or %(prog)s -l lib_store_directory/ [-f]",
                          description="Python to Crystal compiler.")

    parser.add_argument("-w", "--write",
                      action="store_true",
                      dest="output",
                      help="write output *.py => *.cr")

    parser.add_argument("-f", "--force",
                      action="store_true",
                      dest="force",
                      default=False,
                      help="force write output to OUTPUT")

    parser.add_argument("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="verbose option to get more information.")

    parser.add_argument("-s", "--silent",
                      action="store_true",
                      dest="silent",
                      default=False,
                      help="silent option that does not output detailed information.")

    parser.add_argument("-r", "--include-require",
                      action="store_true",
                      dest="include_require",
                      default=True,
                      help="require py2cr library in the output")

    parser.add_argument("-p", "--base-path",
                      action="store",
                      dest="base_path",
                      default=False,
                      help="set default module target path")

    parser.add_argument("-c", "--base-path-count",
                      action="store",
                      dest="base_path_count",
                      type=int,
                      default=0,
                      help="set default module target path nest count")

    parser.add_argument("-m", "--module",
                      action="store_true",
                      dest="mod",
                      default=False,
                      help="convert all local import module files of specified Python file. *.py => *.cr")

    options, args = parser.parse_known_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    filename = args[0]

    # base_dir_path : target python file dir path
    # filename: tests/modules/classname.py
    #  -> base_dir_path: tests/modules/
    if options.base_path:
        base_dir_path = options.base_path
    else:
        base_dir_path = os.path.dirname(filename)
    if options.verbose:
        print("base_dir_path: %s" % base_dir_path)
    mods = {}
    mods_all = {}

    # py_path       : python file path
    def get_mod_path(py_path : str) -> None:
        results = []
        dir_path = os.path.dirname(py_path) if os.path.dirname(py_path) else '.'
        dir_path = os.path.relpath(dir_path, base_dir_path)
        with open(py_path, 'r', encoding="utf-8") as f:
            text = f.read()
            results_f = re.findall(r"^from +([.\w]+) +import +([*\w]+)", text, re.M)
            for res_f in results_f:
                if options.verbose:
                    print("py_path: %s res_f: %s" % (py_path, ', '.join(res_f)))
                if res_f[0] == '.':
                    # from . import hoge
                    res = os.path.normpath(os.path.join(dir_path, res_f[0]))
                elif res_f[0][0] == '.':
                    # from .grandchildren import foo
                    res = os.path.normpath(os.path.join(dir_path, res_f[0][1:]))
                else:
                    # from modules.moda import ModA
                    # => (tests/modules/) modules/moda.py  # => class ModA
                    res = res_f[0]
                if res not in results:
                    results.append(res)
                if res_f[1] != '*':
                    if res_f[0] == '.':
                        # from . import hoge
                        res = os.path.normpath(os.path.join(dir_path, res_f[0], res_f[1]))
                    elif res_f[0][0] == '.':
                        # from .grandchildren import foo
                        res = os.path.normpath(os.path.join(dir_path, res_f[0][1:], res_f[1]))
                    else:
                        # (tests/modules/) modules/moda/ModA.py
                        # (tests/modules/) modules/moda.py
                        res = os.path.normpath(os.path.join(res_f[0], res_f[1]))
                    if res not in results:
                        results.append(res)
            results_f = re.findall(r"^import +([.\w]+)", text, re.M)
            for res_f in results_f:
                # from modules.moda import ModA
                # => (tests/modules/) modules/moda.py  # => class ModA
                # from imported.submodules import submodulea
                # => (tests/modules/) imported/submodules submodulea
                # => require_relative 'submodules/submodulea'
                if res_f == '.':
                    res = dir_path
                else:
                    res = res_f
                if res not in results:
                    results.append(res)
            if options.verbose:
                print("py_path: %s, results: %s" % (py_path, results))
        subfilenames = []
        if results:
            for result in results:
                sf = os.path.normpath(os.path.join(base_dir_path, result.replace('.', '/') + '.py'))
                if options.verbose:
                    print(f"sub_filename: {sf}")
                if sf in subfilenames:
                    continue
                if os.path.exists(sf):
                    if sf not in subfilenames:
                        subfilenames.append(sf)
                    if options.verbose:
                        print(f"[Found]     sub_filename: {sf}")
                    continue
                sf = os.path.join(base_dir_path, result.replace('.', '/'), '__init__.py')
                if sf in subfilenames:
                    continue
                if os.path.exists(sf):
                    if sf not in subfilenames:
                        subfilenames.append(sf)
                    if options.verbose:
                        print(f"[Found]     sub_filename: {sf}")
                    continue
                if options.verbose:
                    print(f"[Not Found] sub_filename: {sf}")
        if options.verbose:
            print("py_path: %s, subfilenames: %s" % (py_path, subfilenames))
        mods[py_path] = subfilenames
        mods_all[py_path] = list(subfilenames)
        for sf in subfilenames:
            if not sf in mods.keys():
                get_mod_path(sf)
                mods_all[py_path].extend(mods[sf])

    # Get all the local import module file names of the target python file
    get_mod_path(filename)

    # Example:
    # tests/modules/classname.py : from modules.moda import ModA     => require_relative 'modules/moda' (Convert using AST)
    #                              => tests/modules/ + modules.moda
    #                              => tests/modules/modules/moda.py
    # -p tests/modules "tests/modules/classname.py"    > "tests/modules/classname.cr"
    # -p tests/modules "tests/modules/modules/moda.py" > "tests/modules/modules/moda.cr"
    if options.verbose:
        for py_path, subfilenames in mods_all.items():
            print(f"mods_all[{py_path}] : {subfilenames}")

    for py_path, subfilenames in mods_all.items():
        if not options.mod:
            if py_path != filename:
                continue

        subfilenames = set(subfilenames)

        output : Optional[str] = None
        if options.output:
            name_path, _ext = os.path.splitext(py_path)
            output = name_path + '.cr'

        if options.verbose:
            print('Try  : ' + py_path + ' : ')
        rtn = convert_py2cr_write(py_path, options.base_path_count, subfilenames,
            base_path=base_dir_path,
            require=options.include_require,
            output=output, force=options.force, no_stop=True, verbose=options.verbose)
        if not options.silent:
            if options.mod or output:
                if output:
                    print('Try  : ' + py_path + ' -> ' + output + ' : ', end='')
                else:
                    print('Try  : ' + py_path + ' : ', end='')
            if options.mod or output:
                if rtn == 0:
                    print('[OK]')
                elif rtn == 1:
                    print('[Warning]')
                elif rtn == 2:
                    print('[Error]')
                elif rtn == 3:
                    print('[Skip]')
                else:
                    print('[Not Defined]')

if __name__ == '__main__':
    main()
