import json
import pathlib

from BlueprintRenderer.CacheHandler import retrieveModData, storeModData
from BlueprintRenderer.DependecyResolver import getDependencyOrder
from BlueprintRenderer.ModLoader import LUA_ENGINE
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

def unpackLuaTable(luaTable):
    d = dict(luaTable)
    for i in d.keys():
        if type(d[i]) in (bool, int, float, str):
            continue
        d[i] = unpackLuaTable(d[i])
    return d


class LuaContext:
    @throwsLuaError
    def __init__(self):
        self.running = False
        self.runtime = LUA_ENGINE.LuaRuntime(max_memory=MAX_LUA_MEMORY)
        self.set_env_variable = self.runtime.eval("function(attribute_name, value) _G[attribute_name] = value; end")
        self.get_env_variable = self.runtime.eval("function(attribute_name) return _G[attribute_name]; end")
        self.init_phase = self.runtime.eval("function(phase_name) return initialize_phase(phase_name); end")
        self.run_phase = self.runtime.eval("function(phase_name) return run_phase(phase_name); end")

    @throwsLuaError
    def runEngine(self):
        path = pathlib.Path(__file__).parent.resolve()
        print(path)
        self.runtime.execute(f"package.path = \"{path}\\?.lua;{path}\\?\";".replace("\\", "\\\\"))
        self.runtime.require("FactorioExecutor2")
        self.running = True

    @throwsLuaError
    def __setitem__(self, key, value):
        if isinstance(value, (list, tuple)):
            value = self.runtime.table_from(value, recursive=True)
        elif isinstance(value, dict):
            value = self.runtime.table_from(value, recursive=True)
        self.set_env_variable(key, value)

    @throwsLuaError
    def __getitem__(self, item):
        result = self.get_env_variable(item)
        return result

    def load_defaults(self):
        self["system_path_seperator"] = os.sep
        self["cache_path_base"] = os.path.join(CACHE, "mods")
        self["dependency_order"] = [i.name for i in getDependencyOrder(MODS)]
        self["cache_path"] = CACHE

    @requiresRunning
    @throwsLuaError
    def initializePhase(self, phase_name):
        return self.init_phase(phase_name)

    @requiresRunning
    @throwsLuaError
    def runPhase(self, phase_name):
        return self.run_phase(phase_name)

    @requiresRunning
    def startGame(self):
        self.initializePhase("settings")
        self.runPhase("settings")
        self.runPhase("settings-updates")
        self.runPhase("settings-final-fixes")
        settings_data = self["raw_data"]

        input_settings_data = {
            "startup": {},
            "runtime-global": {}
        }
        for settings_type in settings_data:
            for setting in settings_data[settings_type]:
                sett = settings_data[settings_type][setting]
                if sett["setting_type"] == "startup":
                    if sett["name"] in MOD_SETTINGS["startup"].keys():
                        input_settings_data["startup"][sett["name"]] = MOD_SETTINGS["startup"][sett["name"]]
                    else:
                        input_settings_data["startup"][sett["name"]] = {"value": sett["default_value"]}
        self["settings"] = input_settings_data
        self.initializePhase("data")
        self.runPhase("data")
        self.runPhase("data-updates")
        self.runPhase("data-final-fixes")
        self.mod_data = unpackLuaTable(self["raw_data"])
        storeModData(self.mod_data)

def getModData():
    ret = retrieveModData()
    if ret is None:
        ctx = LuaContext()
        ctx.load_defaults()
        ctx.runEngine()
        ctx.startGame()
        return ctx.mod_data
    return ret
