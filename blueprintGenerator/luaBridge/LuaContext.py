from blueprintGenerator.dependecyResolver import getDependencyOrder
from configImport import *
import os


def requiresRunning(method):
    def meth(self, *args, **kwargs):
        if not self.running:
            print("trying to run something on not running engine")
            return
        return method(self, *args, **kwargs)

    return meth


def throwsLuaError(method):
    def meth(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except LUA_ENGINE.LuaError as e:
            print(e.__str__())

    return meth


class LuaContext:
    def __init__(self):
        self.runtime = LUA_ENGINE.LuaRuntime()
        self.set_env_variable = self.runtime.eval("function(attribute_name, value) _G[attribute_name] = value; end")
        self.get_env_variable = self.runtime.eval("function(attribute_name) return _G[attribute_name]; end")
        self.execute_phase_ev = self.runtime.eval("function(phase_name) return phase_executor(phase_name); end")
        self.running = False

    @throwsLuaError
    def runEngine(self):
        self.runtime.require("LuaEnvBuilder")
        self.running = True

    @throwsLuaError
    def __setitem__(self, key, value):
        if isinstance(value, (list, tuple)):
            value = self.runtime.table_from(value)
        elif isinstance(value, (dict)):
            value = self.runtime.table_from(value, bool_recursive=True)
        self.set_env_variable(key, value)

    @throwsLuaError
    def __getitem__(self, item):
        result = self.get_env_variable(item)
        return result

    def load_defaults(self):
        self["system_path_seperator"] = os.sep
        self["cache_path_base"] = os.path.join(CACHE, "mods")
        self["dependency_order"] = [i.name for i in getDependencyOrder(MODS)]

    @requiresRunning
    @throwsLuaError
    def initializePhase(self, phase_name):
        return self.execute_phase_ev(phase_name)


ctx = LuaContext()
ctx.load_defaults()
ctx.runEngine()
ctx.initializePhase("settings")
