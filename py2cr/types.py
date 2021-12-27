"""
This module handles conversion of python types to crystal types
"""

from typing import Tuple
import sys
import ast


# note: apparently something changed in the AST between
# python 3.8 and 3.9 here.
def node_slice_value(node):
    pymajor = sys.version_info.major
    pyminor = sys.version_info.minor
    if pymajor >= 3 and pyminor >=9:
        return node.slice
    # older cases...
    return node.slice.value

class CrystalTypes:

    name_map = {
        'bool'  : 'Bool',
        'True'  : 'true',  # python 2.x
        'False' : 'false', # python 2.x
        'None'  : 'Nil',   # python 2.x
        'str'   : 'String',
        'int'   : 'Int32',
        'float' : 'Float64',
        'list'  : 'Array',
        'bytes'  : 'Bytes',
        'List'  : 'Array',
        'tuple' : 'Tuple',
        'dict'  : 'Hash',
        'Dict'  : 'Hash',
    }

    def __init__(self, node) -> None:
        self.node = node

    def unwrap_list(self) -> str:
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "list":
            raise Exception(f"Expecting ast.Subscript value to be a list but got {subscript_name}")
        return self.visit(node.slice)

    def unwrap_tuple(self) -> str:
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "tuple":
            raise Exception(f"Expecting ast.Subscript value to be a tuple but got {subscript_name}")
        return self.visit(node.slice)

    def unwrap_dict(self) -> Tuple[str, str]:
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "dict":
            raise Exception(f"Expecting ast.Subscript value to be a dict but got {subscript_name}")


        nsv = node_slice_value(node)
        if not isinstance(nsv, ast.Tuple):
            raise Exception("Expecting ast.Tuple here and didnt get one.")

        return (self.visit(nsv.elts[0]), self.visit(nsv.elts[1]))



    def visit(self, node = None) -> str:
        if node is None:
            node = self.node
        if isinstance(node, ast.Name):
            return self.visit_Name(node)
        if isinstance(node, ast.Subscript):
            return self.visit_Subscript(node)
        if isinstance(node, ast.Tuple):
            return self.visit_Tuple(node)
        if isinstance(node, ast.Index):
            return self.visit(node.value)
        if isinstance(node, ast.Constant):
            return self.visit_Constant(node)
        if isinstance(node, ast.Attribute):
            return self.visit_Attribute(node)
        raise Exception(f"Unknown klass {type(node)} in CrystalTypes")

    def visit_Attribute(self, node) -> str:
        return self.visit(node.value)
    
    def visit_Name(self, node) -> str:
        """
        Name(identifier id, expr_context ctx)
        """
        nid = node.id
        if nid in self.name_map:
            return self.name_map[nid]
        return str(nid)

    def visit_Tuple(self, node) -> str:
        els = [self.visit(e) for e in node.elts]
        return ", ".join(els)

    def visit_Subscript(self, node) -> str:
        """
        Special handling for Union and Optional types.
        Subscripts for Crystal Annotations use (), not []
        """
        name = self.visit(node.value)

        node_slice = node_slice_value(node)
        if name == "Union":
            pipeargs = [self.visit(e) for e in node_slice.elts]
            pipetypes = " | ".join(pipeargs)
            return f"( {pipetypes} )"
        if name == "Optional":
            return self.visit(node_slice) + "?"
        #return f"{name}({node_slice})"
        #return "%s(%s)" % (self.visit(node.value), self.visit(node.slice))
        typearg = self.visit(node.slice)
        return f"{name}({typearg})"



    def visit_Constant(self, node) -> str:
        const_typename = node.value.__class__.__name__
        if const_typename in self.name_map:
            return self.name_map[const_typename]
        return "_"

    @classmethod
    def constant(cls, node, nilable=True) -> str:
        if isinstance(node, ast.Constant): # py3.8+
            const_typename = node.value.__class__.__name__
        elif isinstance(node, ast.Num):
            const_typename = node.n.__class__.__name__
        elif isinstance(node, ast.Str):
            const_typename = 'str'
        elif isinstance(node, ast.Tuple):
            const_typename = 'tuple'
            els = [str(x.value) for x in node.elts]
            print( ", ".join(els))
        elif isinstance(node, ast.Dict):
            const_typename = 'dict' # node.visit(node)
        elif isinstance(node, ast.Call):
            const_typename = f"{node.func}(#{node.args})"
        elif isinstance(node, ast.Name):
            # unclear what to do here.
            #const_typename = node.id
            const_typename = None
            
        else:
            raise Exception(f"Invalid constant node: {node} at line {node.lineno}")

        if const_typename in cls.name_map:
            crystal_typename = cls.name_map[const_typename]
            if nilable:
                return crystal_typename + "?"
            return crystal_typename
        #else:
        #    return const_typename
        return "_"
