import json
import os
import re

from configImport import *

MOD_MATCH = re.compile("^ *([?!])? *[a-zA-Z0-9_-]+ *((>=|>|=|<|<=) *[0-9]{1,10}\.[0-9]{1,10}\.[0-9]{1,10} *)?$")
MOD_MATCH_SHORT = re.compile("[a-zA-Z0-9_-]+")

class PrimitiveMod:
    def __init__(self, name, dependencies):
        self.name = name
        self.dependencies = dependencies

    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        if other.name in self.dependencies:
            return True
        if self.name in other.dependencies:
            return False
        return self.name > other.name

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return not self >= other

    def __le__(self, other):
        return not self > other

    def __repr__(self):
        return self.name

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


def getDependencyOrder(mods):
    primitiveMods = []
    for i in mods.keys():
        primitiveMods.append(PrimitiveMod(i, retrieveDependencies(i)))
    primitiveMods.sort()
    return primitiveMods

print(getDependencyOrder(ACTIVE_MODS))
