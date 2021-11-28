#from typing import Dict

class CrystalTranslator:
    """Abstract Base Class that other translators inherit from"""
    def __init__(self):
        pass

class TranslatorRegistry:
    def __init__(self):
        # python module-name to translator-subclass
        self.map_pymod_to_klass = {}
        # python module-name to crystal require
        self.map_pymod_to_require = {}

        for klass in CrystalTranslator.__subclasses__():
            obj = klass()
            self.map_pymod_to_klass[obj.python_module_name] = klass
            self.map_pymod_to_require[obj.python_module_name] = obj.crystal_require

    def func_lookup(self, modname : str, attrname : str):
        if modname in self.map_pymod_to_klass:
            klass = self.map_pymod_to_klass[modname]
            if hasattr(klass, attrname):
                return getattr(klass, attrname)
        return None

    def attr_lookup(self, modname : str, attrname : str):
        if modname in self.map_pymod_to_klass:
            klass = self.map_pymod_to_klass[modname]
            try:
                newattr = klass.attribute_map.get(attrname)
                return newattr
            except AttributeError:
                return None
        return None

    def require_lookup_or_none(self, modname : str):
        # a fetch or None if we dont have it.
        return self.map_pymod_to_require.get(modname, None)

    def require_lookup(self, modname : str):
        # If we cannot find a crystal-require for this module, then use the
        # python module-name as-is for the crystal-require
        return self.map_pymod_to_require.get(modname, modname)
    
