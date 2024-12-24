local real_require = require
local path_seperator = system_path_seperator
local cache_path_base = cache_path_base
local dependency_order = dependency_order

function build_env(mod_name)
    local mod_name = mod_name
    local function _require(name)
        package.path = cache_path_base .. system_path_seperator .. mod_name .. system_path_seperator .. "?.lua;E:\\PycharmProjects\\Python-Mod-Bot\\blueprintGenerator\\luaBridge\\LuaFileNotFound.lua";
        local path = name:gsub("%/", path_seperator)
        real_require(path)
        package.path = nil
        return
    end

    local env = {
        -- default factorio variables
        data = {},
        mods = {},
        settings = {},
        feature_flags = {},
        -- standard functions
        print = print,
        require = _require,
        string = {
            sub = string.sub,
            len = string.len,
        }
    }

    return env
end

local envs = {}

for k, v in pairs(dependency_order) do
    envs[v] = build_env(v)
end



function phase_executor(phase_name)
    for k, v in pairs(dependency_order) do
        local status, result = pcall(load, "require('" .. phase_name .. "');os.execute('echo bla;');", v, "t", envs[v])
        if status then
            local status2, result2 = pcall(result)
            if status2 then
                print("successfully ran " .. v)
            else
                print("Error in Mod: " .. v)
                print(result2)
            end
        else
            print("Compile error in Mod: " .. v)
            print(result)
        end
    end
end
