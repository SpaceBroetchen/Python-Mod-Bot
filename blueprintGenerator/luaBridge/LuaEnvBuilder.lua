local real_require = require
local path_seperator = system_path_seperator
local cache_path_base = cache_path_base
local dependency_order = dependency_order


function _require(name)
    print(_G)
    os.execute("echo potentially unsave content!;");
    package.path = cache_path_base .. system_path_seperator .. mod_name .. system_path_seperator .. "?.lua;E:\\PycharmProjects\\Python-Mod-Bot\\blueprintGenerator\\luaBridge\\LuaFileNotFound.lua";
    local path = name:gsub("%/", path_seperator)
    real_require(path)
    package.path = nil
    return
end

env = {
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
print(_G)
print(env)
load("require('" .. "settings" .. "');", nil, "tb", env)()


function phase_executor(phase_name)

end
