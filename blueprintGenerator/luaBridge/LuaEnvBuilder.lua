local real_load_file = loadfile
local path_seperator = system_path_seperator
local cache_path_base = cache_path_base
local dependency_order = dependency_order
package.path = cache_path .. system_path_seperator .. "?.lua;?.lua"
require("TableUtils")
require("api.defines")


loaded_prototypes = 0
raw_data = {}

function build_env(mod_name)
    local mod_name = mod_name

    local env = {
        -- default factorio variables
        data = {
            raw = raw_data
        },
        mods = {},
        settings = {},
        feature_flags = {},
        defines = defines:deepcopy(),
        -- standard functions
        print = print,
        package = {

        },
        string = {
            sub = string.sub,
            byte = string.byte,
            char = string.char,
            len = string.len,
            gsub = string.gsub,
            find = string.find,
            format = string.format
        },
        tostring = tostring,
        table = {
            insert = table.insert
        },
        pairs = pairs,
        ipairs = ipairs,
        math = {
            floor = math.floor,
            sqrt = math.sqrt,
            acos = math.acos,
            pi = math.pi,
            sin = math.sin,
            cos = math.cos,
        },
        type = type,
        getmetatable = getmetatable,
        setmetatable = setmetatable,
        assert = assert
    }

    local require_searches = {
        [1] = cache_path_base .. system_path_seperator .. "!" .. system_path_seperator .. "?.lua",
        [2] = cache_path_base .. system_path_seperator .. "core" .. system_path_seperator .. "lualib" .. system_path_seperator .. "?.lua",
    }

    function env.require(name)
        name = name:gsub("%/", ".")
        local executable = nil
        local mod_name = mod_name
        if name:match("^__%w+__%.") ~= nil then
            local m = name:match("^__%w+__%.")
            mod_name = m:sub(3, m:len() - 3)
            name = name:sub(m:len(), name:len())
        end

        for k, v in pairs(require_searches) do
            name = name:gsub("%.", system_path_seperator)
            executable = real_load_file(v:gsub("%?", name):gsub("%!", mod_name), "t", env)
            if executable ~= nil then
                break
            end
        end

        if executable == nil then
            print("file not found!, " .. name)
        else
            local out = executable()
            --extendDeepTable(env, out, name)
            return out
        end
    end

    function env.data.extend(self, dat)
        if self ~= env.data and dat == nil then
            dat = self
        end

        for _, prototype in ipairs(dat) do
            if prototype.name == nil then
                print("missing prototype name!")
                return
            end
            if prototype.type == nil then
                print("missing prototype type!")
                return
            end

            print("registering prototype: " .. prototype.name .. " (" .. prototype.type .. ")")

            local ptable = env.data.raw[prototype.type] or {}
            env.data.raw[prototype.type] = ptable
            ptable[prototype.name] = prototype
            loaded_prototypes = loaded_prototypes + 1
        end
    end

    return env
end
