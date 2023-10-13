local opauth_root = "{$OPAUTH_ROOT}"
local opauth_cpath = opauth_root.."/lua/?.lua;"..opauth_root.."/lua/?.lua;"..opauth_root.."/lua/?.lua;"
local opauth_sopath = opauth_root.."/lua/?.so;"

if not package.path:find(opauth_cpath) then
    package.path = opauth_cpath .. package.path
end

if not package.cpath:find(opauth_sopath) then
    package.cpath = opauth_sopath .. package.cpath
end