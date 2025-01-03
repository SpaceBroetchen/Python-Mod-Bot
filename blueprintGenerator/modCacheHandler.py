import hashlib
import shutil
import zipfile

from configImport import *
import os

default_mods = {"base", "core", "space-age", "elevated-rails", "quality"}

MOD_CACHE = os.path.join(CACHE, "mods")


def hashModDictionary(mods):
    l = []
    for i in mods.keys():
        l.append(f"{i}=={mods[i]}")
    return hashlib.md5(";".join(l).encode(encoding='UTF-8')).hexdigest()


def locateSource(mod, version):
    if mod in default_mods:
        path = os.path.join(FACTORIO_DATA, mod)
    else:
        path = os.path.join(FACTORIO_MOD_FOLDER, f"{mod}_{version}")
        if not os.path.exists(path):
            path += ".zip"

    if not os.path.exists(path):
        print(f"Missing {mod}=={version}")
        return None
    return path


def copyMod(mod, version):
    source = locateSource(mod, version)
    if source is None:
        return False
    if os.path.isdir(source):
        shutil.copytree(source, os.path.join(MOD_CACHE, mod))
        return True
    shutil.copy(source, MOD_CACHE)
    with zipfile.ZipFile(os.path.join(MOD_CACHE, os.path.basename(source))) as z:
        z.extractall(MOD_CACHE)
    os.remove(os.path.join(MOD_CACHE, os.path.basename(source)))
    if os.path.exists(os.path.join(MOD_CACHE, mod)):
        return True
    os.renames(os.path.join(MOD_CACHE, os.path.splitext(os.path.basename(source))[0]), os.path.join(MOD_CACHE, mod))
    return True


def createModCache():
    clearModCache()
    if not os.path.exists(MOD_CACHE):
        os.mkdir(MOD_CACHE)
    fails = 0
    success = 0
    active = {}
    for i in MODS.keys():
        if copyMod(i, MODS[i]):
            success += 1
            active[i] = MODS[i]
        else:
            fails += 1
    print(f"loaded {success} mods successfully, failed {fails}")
    print(f"current mod hash: {hashModDictionary(active)}")


def clearModCache():
    shutil.rmtree(MOD_CACHE)


createModCache()
