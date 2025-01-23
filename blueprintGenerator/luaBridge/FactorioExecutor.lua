package.path = cache_path .. system_path_seperator .. "?.lua;?.lua"
require("LuaEnvBuilder")

function initialize_phase(name)
    print("Initializing phase " .. name)
    envs = {}
    for k, v in pairs(dependency_order) do
        envs[v] = build_env(v, settings)
    end
    if name == "data" then
        TableUtils.print(settings, 4)
    end
end

function run_phase(name)
    print("running phase: " .. name)
    for k, v in pairs(dependency_order) do
        local file = loadfile("E:\\PycharmProjects\\Python-Mod-Bot\\cache\\mods\\" .. v .. "\\" .. name .. ".lua", "t", envs[v])
        if file ~= nil then
            print("    loading: " .. v)
            file()
        end
    end


end