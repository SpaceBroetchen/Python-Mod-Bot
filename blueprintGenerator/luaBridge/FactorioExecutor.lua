



env1 = build_env("core")
env2 = build_env("base")
file = loadfile("E:\\PycharmProjects\\Python-Mod-Bot\\cache\\mods\\core\\data.lua", "t", env1)
file()
file = loadfile("E:\\PycharmProjects\\Python-Mod-Bot\\cache\\mods\\base\\data.lua", "t", env2)
file()
print("loaded " .. tostring(loaded_prototypes) .. " prototypes!")