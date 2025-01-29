package.path = package.path .. ";" .. cache_path .. system_path_seperator .. "?.lua;?.lua"
local real_load_file = loadfile
local path_seperator = system_path_seperator
local cache_path_base = cache_path_base
local dependency_order = dependency_order
require("TableUtils")
require("api.defines")
serpent = require("serpent")

raw_data = {}
loaded_prototypes = 0

local env = {
    -- factorio variables
    data = {
        raw = raw_data
    },
    mods = {},
    feature_flags = raw_data,
    defines = TableUtils.deepcopy(defines),
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
        insert = table.insert,
        deepcopy = table.deepcopy,
        sort = table.sort,
        remove = table.remove
    },
    pairs = pairs,
    ipairs = ipairs,
    next = next,
    math = {
        floor = math.floor,
        sqrt = math.sqrt,
        asin = math.asin,
        acos = math.acos,
        atan = math.atan,
        atan2 = math.atan2,
        pi = math.pi,
        sin = math.sin,
        cos = math.cos,
        tan = math.tan,
        abs = math.abs,
        max = math.max,
        min = math.min,
        ceil = math.ceil,
    },
    type = type,
    getmetatable = getmetatable,
    setmetatable = setmetatable,
    assert = assert,
    __active__ = nil,
    serpent = {
        block = serpent.block;
    },
    log = function(string)
        print(string)
    end
}

local require_searches = {
    [1] = cache_path_base .. system_path_seperator .. "!" .. system_path_seperator .. "?.lua",
    [2] = cache_path_base .. system_path_seperator .. "core" .. system_path_seperator .. "lualib" .. system_path_seperator .. "?.lua",
}

function env.require(name)
    local old_name = env.__active__;
    name = name:gsub("%/", ".")
    local executable = nil
    local mod_name = env.__active__
    if name:match("^__[%w%-_]+__%.") ~= nil then
        local m = name:match("^__[%w%-_]+__%.")
        mod_name = m:sub(3, m:len() - 3)
        name = name:sub(m:len(), name:len())
    end

    for k, v in pairs(require_searches) do
        name = name:gsub("%.", system_path_seperator)
        env.__active__ = mod_name
        executable = real_load_file(v:gsub("%?", name):gsub("%!", mod_name), "t", env)
        if executable ~= nil then
            break
        end
    end

    if executable == nil then
        print("file not found!, " .. name .. ", from mod: " .. old_name)
        error("Here is an error")

    else
        local out = executable()
        --extendDeepTable(env, out, name)
        env.__active__ = old_name;
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

        --print("registering prototype: " .. prototype.name .. " (" .. prototype.type .. ")")

        local ptable = env.data.raw[prototype.type] or {}
        env.data.raw[prototype.type] = ptable
        ptable[prototype.name] = prototype
        loaded_prototypes = loaded_prototypes + 1
        print(prototype.name)
    end
end


function initialize_phase(name)
    print("Initializing phase " .. name)
end

function run_phase(name)
    print("running phase: " .. name)
    if name == "data" then
        env.settings = settings;
    end
    for k, v in pairs(dependency_order) do
        env.__active__ = v;

        local file = loadfile("E:\\PycharmProjects\\Python-Mod-Bot\\cache\\mods\\" .. v .. "\\" .. name .. ".lua", "t", env)
        if file ~= nil then
            print("    loading: " .. v)
            file()
        end
    end


end