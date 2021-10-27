import ast
from .translator import *

class Os(CrystalTranslator):
    attribute_map = {
        "environ": "PyOs.environ"
    }
    def __init__(self):
        self.python_module_name = "os"
        self.crystal_require = None
        
    def walk(funcdb):
        return funcdb.wrap_class_method("PyOs", "walk")

    def getenv(funcdb):
        return funcdb.wrap_class_method("PyOs", "getenv")

class OsPath(CrystalTranslator):
    def __init__(self):
        self.python_module_name = "os.path"
        self.crystal_require = None
        
    def dirname(funcdb):
        return funcdb.wrap_class_method("File", "dirname")

    def basename(funcdb):
        return funcdb.wrap_class_method("File", "basename")

    def join(funcdb):
        return funcdb.wrap_class_method("File", "join")

