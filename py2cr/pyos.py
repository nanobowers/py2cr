#import ast
from .translator import CrystalTranslator

class Os(CrystalTranslator):
    attribute_map = {
        "environ": "PyOs.environ"
    }
    def __init__(self):
        super().__init__()
        self.python_module_name = "os"
        self.crystal_require = None

    @staticmethod
    def walk(funcdb):
        return funcdb.wrap_class_method("PyOs", "walk")

    @staticmethod
    def getenv(funcdb):
        return funcdb.wrap_class_method("PyOs", "getenv")

class OsPath(CrystalTranslator):
    def __init__(self):
        super().__init__()
        self.python_module_name = "os.path"
        self.crystal_require = None

    @staticmethod
    def dirname(funcdb):
        return funcdb.wrap_class_method("File", "dirname")

    @staticmethod
    def basename(funcdb):
        return funcdb.wrap_class_method("File", "basename")

    @staticmethod
    def join(funcdb):
        return funcdb.wrap_class_method("File", "join")
