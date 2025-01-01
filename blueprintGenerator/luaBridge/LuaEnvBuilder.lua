local real_load_file = loadfile
local path_seperator = system_path_seperator
local cache_path_base = cache_path_base
local dependency_order = dependency_order
package.path = cache_path .. system_path_seperator .. "?.lua"
require("api.defines")


local mod_name = "base"


function extendDeepTable(table, value, path)
    matches = path:gmatch("([^.]+)")
    for w in matches do
        t = table[w] or {}
        table[w] = t
        table = t
        l = w
    end
    table[l] = value
end

function printDeepTable(table, max_depth, offset, key)
    max_depth = max_depth or 10
    offset = offset or 0
    if key == nil then
        key = ""
    else
        key = '"' .. tostring(key) .. '" '
    end
    if next(table) == nil then
        print(("    "):rep(offset) .. key .. tostring(table) .. " []")
    else
        if max_depth == offset then
            print(("    "):rep(offset) .. key .. tostring(table) .. ": [...]")
        else
            print(("    "):rep(offset) .. key .. tostring(table) .. ":")
            for k, v in pairs(table) do
                if (type(v) == "table") then
                    printDeepTable(v, max_depth, offset + 1, k)
                else
                    print(("    "):rep(offset + 1) .. '"' .. tostring(k) .. "\": " .. tostring(v))
                end
            end
        end
    end
end

function build_env(mod_name)
    local mod_name = mod_name

    local env = {
        -- default factorio variables
        data = {
            extend = function(...)
                print("extending data")
            end
        },
        mods = {},
        settings = {},
        feature_flags = {},
        defines = defines,


        -- standard functions
        print = print,
        string = {
            sub = string.sub,
            len = string.len,
        },
        tostring = tostring,
        table = {
            deepcopy = table.deepcopy
        },
        pairs = pairs,
        math = {
            floor = math.floor
        }
    }

    local require_searches = {
        [1] = cache_path_base .. system_path_seperator .. mod_name .. system_path_seperator .. "?.lua",
        [2] = cache_path_base .. system_path_seperator .. "core" .. system_path_seperator .. "lualib" .. system_path_seperator .. "?.lua",
    }

    function _require(name)
        name = name:gsub("%.", system_path_seperator)
        for k, v in pairs(require_searches) do
            executable = real_load_file(v:gsub("%?", name), "t", env)
            if executable ~= nil then
                break
            end
        end
        if executable == nil then
            print("file not found!, " .. name)
        else
            out = executable()
            extendDeepTable(env, out, name)
        end
    end

    env["require"] = _require;
    return env
end

env = build_env(mod_name)
file = loadfile("E:\\PycharmProjects\\Python-Mod-Bot\\blueprintGenerator\\luaBridge\\PotentiallyUnsafeLuaFileForTest.lua", "t", env)
file()

function phase_executor(phase_name)

end
