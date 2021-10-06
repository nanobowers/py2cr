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
