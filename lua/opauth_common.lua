
local cjson = require "cjson"

local ok, new_tab = pcall(require, "table.new")
if not ok or type(new_tab) ~= "function" then
    new_tab = function (narr, nrec) return {} end
end

local setmetatable = setmetatable
local _M = { _VERSION = '1.0' }
local mt = { __index = _M }

function _M.new(self, opts)
    opts = opts or {}
    local log_dir = opts.log_dir or '/tmp'
    local salt = opts.salt or 'salt'
    local cdn_headers = opts.cdn_headers or {
        [1] = "x-forwarded-for",
        [2] = "x-real-ip",
        [3] = "x-forwarded",
        [4] = "forwarded-for",
        [5] = "forwarded",
        [6] = "true-client-ip",
        [7] = "client-ip",
        [8] = "ali-cdn-real-ip",
        [9] = "cdn-src-ip",
        [10] = "cdn-real-ip",
        [11] = "cf-connecting-ip",
        [12] = "x-cluster-client-ip",
        [13] = "wl-proxy-client-ip",
        [14] = "proxy-client-ip",
        [15] = "true-client-ip"
    }
    return setmetatable({
            log_dir = log_dir,
            salt = salt,
            cdn_headers = cdn_headers
    }, mt)
end
-- 调试方式
function _M.D(self, msg)
    local _msg = ''
    -- ngx.say(type(msg))
    if type(msg) == 'table' then
        for key, val in pairs(msg) do
            _msg = _msg..tostring(key)..':'..tostring(val).."|\n"
        end
        if _msg == '' then
            _msg = "\n"
        else 
            _msg = "args->\n|".._msg
        end
    elseif type(msg) == 'string' then
        _msg = msg.."\n"
    elseif type(msg) == 'nil' then
        _msg = 'nil'.."\n"
    else
        _msg = msg.."\n"
    end

    local fp = io.open(self.log_dir.."/debug.log", "ab")
    if fp == nil then
        return nil
    end

    local localtime = ngx.localtime()
    fp:write(localtime..":"..tostring(_msg))
    
    fp:flush()
    fp:close()
    return true
end


function _M.split(self, str, reps)
    local arr = {}
    string.gsub(str,'[^'..reps..']+',function(w) table.insert(arr,w) end)
    return arr
end

function _M.arrlen(self, arr)
    if not arr then return 0 end
    local count = 0
    for _,v in ipairs(arr) do
        count = count + 1
    end
    return count
end

function _M.is_ipaddr(self, client_ip)
    local cipn = self:split(client_ip,'.')
    if self:arrlen(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end


function _M.get_client_ip(self)
    local client_ip = "unknown"
    local request_header = ngx.req.get_headers()

    for _,v in ipairs(self.cdn_headers) do
        if request_header[v] ~= nil and request_header[v] ~= "" then
            local ip_list = request_header[v]
            client_ip = self:split(ip_list,',')[1]
            break;
        end
    end


    -- ipv6
    if type(client_ip) == 'table' then client_ip = "" end
    if client_ip ~= "unknown" and ngx.re.match(client_ip,"^([a-fA-F0-9]*):") then
        return client_ip
    end

    -- ipv4
    if  not ngx.re.match(client_ip,"\\d+\\.\\d+\\.\\d+\\.\\d+") == nil or not self:is_ipaddr(client_ip) then
        client_ip = ngx.var.remote_addr
        if client_ip == nil then
            client_ip = "unknown"
        end
    end

    return client_ip
end

function _M.rand(self)
    local str = ngx.md5(ngx.time() .. self.salt)
    return str
end


return _M