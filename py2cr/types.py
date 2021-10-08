import ast

class CrystalTypes:

    name_map = {
        'True'  : 'true',  # python 2.x
        'False' : 'false', # python 2.x
        'None'  : 'nil',   # python 2.x
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
        return self.visit(node.slice.value)
        
    def unwrap_dict(self):
        node = self.node
        # expect node to be something to unwrap
        if not isinstance(node, ast.Subscript):
            raise Exception(f"Expecting a ast.Subscript to unwrap, got {type(node)}")
        # check that subscript value
        subscript_name = str(node.value.id)
        if subscript_name.lower() != "dict":
            raise Exception(f"Expecting ast.Subscript value to be a dict but got {subscript_name}")
        nsv = node.slice.value
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
        if name == "Union":
            pipeargs = [self.visit(e) for e in node.slice.value.elts]
            pipetypes = " | ".join(pipeargs)
            return "( " + pipetypes + " )"
        elif name == "Optional":
            return self.visit(node.slice.value) + "?"
        else:
            return "%s(%s)" % (self.visit(node.value), self.visit(node.slice))
