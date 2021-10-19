import sys
import ast

# apparently something changed in the AST between
# python 3.8 and 3.9 here.
def node_slice_value(node):
    pymajor = sys.version_info.major
    pyminor = sys.version_info.minor
    if pymajor >= 3 and pyminor >=9:
        return node.slice
    else:
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
        'List'  : 'Array',
        'tuple' : 'Tuple',
        'dict'  : 'Hash',
        'Dict'  : 'Hash',
    }

    def __init__(self, node):
        self.node = node

    def unwrap_list(self):
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "list":
            raise Exception(f"Expecting ast.Subscript value to be a list but got {subscript_name}")
        return self.visit(node.slice)

    def unwrap_tuple(self):
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "tuple":
            raise Exception(f"Expecting ast.Subscript value to be a tuple but got {subscript_name}")
        return self.visit(node.slice)
        
    def unwrap_dict(self):
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
            raise

        return (self.visit(nsv.elts[0]), self.visit(nsv.elts[1]))


        
    def visit(self, node = None):
        if node is None:
            node = self.node
        if isinstance(node, ast.Name):
            return self.visit_Name(node)
        elif isinstance(node, ast.Subscript):
            return self.visit_Subscript(node)
        elif isinstance(node, ast.Tuple):
            return self.visit_Tuple(node)
        elif isinstance(node, ast.Index):
            return self.visit(node.value)
        elif isinstance(node, ast.Constant):
            return self.visit_Constant(node)
        else:
            raise Exception("Unknown klass %s in CrystalTypes" % type(node))
        
    def visit_Name(self, node):
        """
        Name(identifier id, expr_context ctx)
        """
        nid = node.id
        if nid in self.name_map:
            return self.name_map[nid]
        return str(nid)

    def visit_Tuple(self, node):
        els = [self.visit(e) for e in node.elts]
        return ", ".join(els)
        
    def visit_Subscript(self, node):
        """
        Special handling for Union and Optional types.
        Subscripts for Crystal Annotations use (), not []
        """
        name = self.visit(node.value)

        node_slice = node_slice_value(node)
        if name == "Union":
            pipeargs = [self.visit(e) for e in node_slice.elts]
            pipetypes = " | ".join(pipeargs)
            return "( " + pipetypes + " )"
        elif name == "Optional":
            return self.visit(node_slice) + "?"
        else:
            return "%s(%s)" % (self.visit(node.value), self.visit(node.slice))

    def visit_Constant(self, node):
        const_typename = node.value.__class__.__name__
        if const_typename in self.name_map:
            return self.name_map[const_typename]
        return "_"
        
    @classmethod
    def constant(cls, node, nilable=True):
        #if not hasattr(node, "value"):
        #    return "_"
        const_typename = node.value.__class__.__name__
        if const_typename in cls.name_map:
            crystal_typename = cls.name_map[const_typename]
            if nilable:
                return crystal_typename + "?"
            else:
                return crystal_typename
        else:
            return "_"
        
