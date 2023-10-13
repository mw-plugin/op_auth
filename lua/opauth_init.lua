
local oa_debug_log_dir = '{$OPAUTH_ROOT}'

local opauth_conf = require('opauth_conf')
local opauth_common = require('opauth_common')
local op_common = opauth_common:new({
	log_dir = oa_debug_log_dir,
	salt = opauth_conf.salt
})

local json = require "cjson"
local aes = require "resty.aes"
-- ngx.say(json.encode(opauth_conf))

local function oa_run()
	-- ngx.header.content_type = "text/html"
	-- ngx.say(opauth_conf.cache_enable)
	if opauth_conf.cache_enable == 0 then
		return false
	end

	local oa_remote_addr = op_common:get_client_ip()
	local op_key = opauth_conf.cache_key_prefix ..oa_remote_addr
	local op_pass_key = opauth_conf.cache_key_prefix..'pass_'..oa_remote_addr

	local uri_request_args = ngx.req.get_uri_args()
	local aes_128_cbc_with_iv = assert(aes:new(opauth_conf.aes_key, nil, aes.cipher(128,"ecb"), {iv=opauth_conf.aes_iv}))

	-- local token_de,err = aes_128_cbc_with_iv:decrypt(tokenText)
	-- ngx.say("token_de de:",token_de, "\n")
	-- ngx.say("oa_rand:",oa_rand(), "\n")

	local op_redis = require('opauth_redis')
	local red = op_redis:new({
		ip = opauth_conf.redis_ip,
		port = opauth_conf.redis_port,
		password = opauth_conf.redis_password,
		db_index = opauth_conf.redis_db_index
	})

    -- local now_url = string.gsub(ngx.var.uri, "/", "-")
    -- ngx.say("url:",now_url,"\n")

    -- get token
    if ngx.var.uri == '/'..opauth_conf.api_get_path then
    	ngx.header.content_type = "application/json"
    	local rdata = {}
		-- local token_aes, err = aes_128_cbc_with_iv:encrypt("123123")
		local r = op_common:rand()
    	local token_aes, err = aes_128_cbc_with_iv:encrypt(r)
    	if err then
    		rdata['code'] = -1
    		rdata['msg'] = 'busy!'
    		ngx.say(json.encode(rdata))
	    	ngx.exit(200)
    		return true
    	end
		local token_aes_b64 = ngx.encode_base64(token_aes)
	
		rdata['msg'] = token_aes_b64
		-- rdata['rand'] = r
		rdata['code'] = 0

		red:setex(op_key, 100, r)
	    ngx.say(json.encode(rdata))
	    ngx.exit(200)
    	return true
   	end

   	local pass_val = red:get(op_pass_key)
   	if pass_val == '1' then
   		return true
   	end

   	-- check token
   	local token = uri_request_args[opauth_conf.api_verify_sign]
   	if token then
   		local op_val = red:get(op_key)
   		if op_val == token then
   			red:setex(op_pass_key, opauth_conf.api_validity_period, '1')
   			red:del(op_key)
   			return true
   		end
   	end
   	ngx.exit(404)
	return true
end

oa_run()

