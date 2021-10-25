class CrystalTranslator:
    def __init__(self):
        pass

class TranslatorRegistry:
    def __init__(self):
        self.map_name_to_klass = {}
        for klass in CrystalTranslator.__subclasses__():
            obj = klass()
            self.map_name_to_klass[obj.klassname] = klass

    def lookup(self, modname, attrname):
        if modname in self.map_name_to_klass:
            klass = self.map_name_to_klass[modname]
            if hasattr(klass, attrname):
                z = getattr(klass, attrname)
                print(z)
            
        
    

registry = TranslatorRegistry()
