import json
import os
import re

from configImport import *
from blueprintGenerator.Mod import Mod

MOD_MATCH = re.compile("^ *([?!])? *[a-zA-Z0-9_-]+ *((>=|>|=|<|<=) *[0-9]{1,10}\.[0-9]{1,10}\.[0-9]{1,10} *)?$")
MOD_MATCH_SHORT = re.compile("[a-zA-Z0-9_-]+")

def parseDependencyString(string):
    if "!" in string:  # ignored, actual check is done by factorio
        return None
    if MOD_MATCH.match(string) is None:
        return None
    return MOD_MATCH_SHORT.search(string).group()


def retrieveDependencies(mod):
    if mod == "base":
        return ["core"]  # since base doesn't contain core by default it will be added here to match

    with open(os.path.join(CACHE, "mods", mod, "info.json")) as f:
        content = json.load(f)

    out = []
    for i in content["dependencies"]:
        p = parseDependencyString(i)
        if p is not None:
            out.append(p)
    return out


def isDependencyFulfilled(mod, activeDependencies, all_mods):
    found_dependencies = 0
    for i in mod.dependencies:
        if not any([i == j.name for j in all_mods]):
            found_dependencies += 1
            continue
        for j in activeDependencies:
            if i == j.name:
                found_dependencies += 1
                break
    return found_dependencies == len(mod.dependencies)


def getDependencyOrder(mods):
    mod_list = []
    for i in mods.keys():
        mod_list.append(Mod(i, retrieveDependencies(i)))
    full_mod_list = mod_list.copy()
    return_mod_list = []
    while len(mod_list) > 0:
        possibilities = list(filter(lambda x: isDependencyFulfilled(x, return_mod_list, full_mod_list), mod_list))
        possibilities.sort()
        mod_list.remove(possibilities[0])
        return_mod_list.append(possibilities[0])
    return return_mod_list
