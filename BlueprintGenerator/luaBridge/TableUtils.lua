
TableUtils = {}

function TableUtils.extend(table, value, path)
    matches = path:gmatch("([^.]+)")
    for w in matches do
        t = table[w] or {}
        table[w] = t
        table = t
        l = w
    end
    table[l] = value
end

function TableUtils.print(t, max_depth, offset, key)
    max_depth = max_depth or 10
    offset = offset or 0
    if key == nil then
        key = ""
    else
        key = '"' .. tostring(key) .. '" '
    end
    if next(t) == nil then
        print(("    "):rep(offset) .. key .. tostring(t) .. " []")
    else
        if max_depth == offset then
            print(("    "):rep(offset) .. key .. tostring(t) .. ": [...]")
        else
            print(("    "):rep(offset) .. key .. tostring(t) .. ":")
            for k, v in pairs(t) do
                if (type(v) == "table") then
                    TableUtils.print(v, max_depth, offset + 1, k)
                else
                    print(("    "):rep(offset + 1) .. '"' .. tostring(k) .. "\": " .. tostring(v))
                end
            end
        end
    end
end

function TableUtils.deepcopy(t)
    local out = {}

    for k, v in pairs(t) do
        if type(k) == "table" then
            k = TableUtils.deepcopy(k)
        end
        if type(v) == "table" then
            v = TableUtils.deepcopy(v)
        end
        out[k] = v
    end
    return out
end