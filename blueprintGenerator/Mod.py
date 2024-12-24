from configImport import *
import os

class Mod:
    def __init__(self, name, dependencies):
        self.name = name
        self.dependencies = dependencies
        self.source_root = os.path.join(CACHE, "mods", name)

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

