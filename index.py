# coding:utf-8

import sys
import io
import os
import time
import re
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'op_auth'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()

    return '/etc/init.d/' + getPluginName()


sys.path.append(getPluginDir() + "/class")
from luamaker import luamaker


def listToLuaFile(path, lists):
    content = luamaker.makeLuaTable(lists)
    content = "return " + content
    mw.writeFile(path, content)


def htmlToLuaFile(path, content):
    content = "return [[" + content + "]]"
    mw.writeFile(path, content)


def restartWeb():
    mw.opWeb('stop')
    mw.opWeb('start')


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]
    return tmp


def contentReplace(content):
    service_path = mw.getServerDir()
    oa_root = getServerDir()
    oa_lua_path = oa_root + "/lua"
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$OPAUTH_ROOT}', oa_root)
    content = content.replace('{$OPAUTH_LUA_DIR}', oa_lua_path)

    return content


def dstLuaPath():
    root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'
    return root_access_dir + '/opauth_init.lua'


def getLocalAndCheckRedisConf():
    path = mw.getServerDir()
    redis_path = path + '/redis'
    redis_gets = ['bind', 'port', 'timeout', 'maxclients',
                  'databases', 'requirepass', 'maxmemory']

    result = {}
    if os.path.exists(redis_path):
        conf = redis_path + '/redis.conf'
        content = mw.readFile(conf)
        for g in redis_gets:
            rep = "^(" + g + ')\s*([.0-9A-Za-z_& ~]+)'
            tmp = re.search(rep, content, re.M)
            if not tmp:
                result[g] = ''
                continue
            result[g] = tmp.groups()[1]
    return result


def initRedisConf(redis_reload=False):
    path = getServerDir()

    source_redis_conf = getLocalAndCheckRedisConf()

    init_data = {}
    init_data['cache_enable'] = 0
    init_data['cache_key_prefix'] = 'opauth_'

    init_data['redis_ip'] = '127.0.0.1'
    init_data['redis_port'] = 6378
    init_data['redis_password'] = ''
    init_data['redis_db_index'] = 0

    # print(source_redis_conf)
    if 'bind' in source_redis_conf:
        init_data['redis_ip'] = source_redis_conf['bind']

    if 'port' in source_redis_conf:
        init_data['redis_port'] = int(source_redis_conf['port'])

    if 'requirepass' in source_redis_conf:
        init_data['redis_password'] = source_redis_conf['requirepass']

    init_data['aes_key'] = mw.getRandomString(16)
    init_data['aes_iv'] = mw.getRandomString(16)
    init_data['salt'] = 'opauth'

    init_data['api_get_path'] = 'opauth_get_token'
    init_data['api_get_enable'] = 1
    init_data['api_jsonp_name'] = 'callback'
    init_data['api_verify_sign'] = 'token'
    init_data['api_validity_period'] = 2 * 3600

    # config
    opauth_cfg = path + '/config.json'
    if not os.path.exists(opauth_cfg):
        mw.writeFile(opauth_cfg, mw.getJson(init_data))

    # 增加参数，利于更新
    if os.path.exists(opauth_cfg):
        data = mw.readFile(opauth_cfg)
        data_json = json.loads(data)

        for k in init_data:
            if not k in data_json:
                data_json[k] = init_data[k]
        mw.writeFile(opauth_cfg, mw.getJson(data_json))

    if os.path.exists(opauth_cfg):
        dst_conf = path + '/lua/opauth_conf.lua'
        data = mw.readFile(opauth_cfg)
        listToLuaFile(dst_conf, json.loads(data))
    return True


def initDreplace():
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'
    # root_worker_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_worker_by_lua_file'
    # root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'
    path = getServerDir()
    path_tpl = getPluginDir()

    opauth_preload = root_init_dir + '/opauth_preload.lua'
    if not os.path.exists(opauth_preload):
        app_tpl = path_tpl + "/lua/opauth_preload.lua"
        content = mw.readFile(app_tpl)
        content = contentReplace(content)
        mw.writeFile(opauth_preload, content)

    dst_lua_dir = path + '/lua'
    if not os.path.exists(dst_lua_dir):
        os.mkdir(dst_lua_dir)

    # redis
    opauth_redis = dst_lua_dir + '/opauth_redis.lua'
    # if not os.path.exists(opauth_redis):
    app_tpl = path_tpl + "/lua/opauth_redis.lua"
    content = mw.readFile(app_tpl)
    content = contentReplace(content)
    mw.writeFile(opauth_redis, content)

    # common
    opauth_common = dst_lua_dir + '/opauth_common.lua'
    app_tpl = path_tpl + "/lua/opauth_common.lua"
    content = mw.readFile(app_tpl)
    content = contentReplace(content)
    mw.writeFile(opauth_common, content)

    initRedisConf()

    return ''


def status():
    opauth_init = dstLuaPath()
    if not os.path.exists(opauth_init):
        return 'stop'
    return 'start'


def oaOp(method):
    return 'ok'


def start():
    initDreplace()
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'
    root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'
    path = getServerDir()
    path_tpl = getPluginDir()

    opauth_preload = root_init_dir + '/opauth_preload.lua'
    if not os.path.exists(opauth_preload):
        app_tpl = path_tpl + "/lua/opauth_preload.lua"
        content = mw.readFile(app_tpl)
        content = contentReplace(content)
        mw.writeFile(opauth_preload, content)

    opauth_init = dstLuaPath()
    if not os.path.exists(opauth_init):
        opauth_init_tpl = path_tpl + "/lua/opauth_init.lua"
        content = mw.readFile(opauth_init_tpl)
        content = contentReplace(content)
        mw.writeFile(opauth_init, content)

    mw.opLuaMakeAll()
    restartWeb()
    return 'ok'


def stop():
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'

    opauth_init = dstLuaPath()
    if os.path.exists(opauth_init):
        os.remove(opauth_init)

    opauth_preload = root_init_dir + '/opauth_preload.lua'
    if os.path.exists(opauth_preload):
        os.remove(opauth_preload)
    mw.opLuaMakeAll()
    restartWeb()
    return 'ok'


def restart():
    restartWeb()
    return 'ok'


def reload():
    initDreplace()
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'
    root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'
    path = getServerDir()
    path_tpl = getPluginDir()

    # preload
    opauth_preload = root_init_dir + '/opauth_preload.lua'
    app_tpl = path_tpl + "/lua/opauth_preload.lua"
    content = mw.readFile(app_tpl)
    content = contentReplace(content)
    mw.writeFile(opauth_preload, content)

    # init
    opauth_init = dstLuaPath()
    opauth_init_tpl = path_tpl + "/lua/opauth_init.lua"
    content = mw.readFile(opauth_init_tpl)
    content = contentReplace(content)
    mw.writeFile(opauth_init, content)

    mw.opLuaMakeAll()
    restartWeb()
    return 'ok'


def installPreInspection():
    return 'ok'


def getRedisConf():
    path = getServerDir() + '/config.json'
    content = mw.readFile(path)
    data = json.loads(content)

    gets = [
        {'name': 'cache_enable', 'type': 0, 'ps': '是否开启缓存'},
        {'name': 'redis_ip', 'type': 2, 'ps': 'Redis地址'},
        {'name': 'redis_port', 'type': 2, 'ps': 'Redis端口'},
        {'name': 'redis_password', 'type': 2, 'ps': 'Redis密码'},
        {'name': 'redis_db_index', 'type': 2, 'ps': 'Redis选择'},
        {'name': 'cache_key_prefix', 'type': 2, 'ps': '缓存KEY前缀'},
    ]

    result = []
    for g in gets:
        n = g['name']
        if n in data:
            g['value'] = data[n]
            result.append(g)
    # print(result)
    return mw.getJson(result)


def getAesConf():
    path = getServerDir() + '/config.json'
    content = mw.readFile(path)
    data = json.loads(content)

    gets = [
        {'name': 'aes_key', 'type': 2, 'ps': 'AES算法KEY值'},
        {'name': 'aes_iv', 'type': 2, 'ps': 'AES算法IV值'},
        {'name': 'salt', 'type': 2, 'ps': '随机数Salt'},
    ]

    result = []
    for g in gets:
        n = g['name']
        if n in data:
            g['value'] = data[n]
            result.append(g)
    # print(result)
    return mw.getJson(result)


def getApiConf():
    path = getServerDir() + '/config.json'
    content = mw.readFile(path)
    data = json.loads(content)

    gets = [
        {'name': 'api_get_enable', 'type': 3, 'ps': '获取Token(json,jsonp)或者关闭',
            'select': [
                {'value': 0, 'name': "关闭"},
                {'value': 1, 'name': "JSON"},
                {'value': 2, 'name': "JSONP"}
            ],
         },
        {'name': 'api_jsonp_name', 'type': 2, 'ps': '开启jsonp有效,jsonp回调名称'},
        {'name': 'api_get_path', 'type': 2, 'ps': '获取Token路径'},
        {'name': 'api_verify_sign', 'type': 2, 'ps': 'Query参数验证名称'},
        {'name': 'api_validity_period', 'type': 2, 'ps': 'API有效期(秒)'},
    ]

    result = []
    for g in gets:
        n = g['name']
        if n in data:
            g['value'] = data[n]
            result.append(g)
    # print(result)
    return mw.getJson(result)


def submitConf():
    gets = [
        'cache_enable', 'redis_ip', 'redis_port',
        'redis_password', 'redis_db_index',
        'aes_key', 'aes_iv', 'salt'
        'api_get_path', 'api_verify_sign', 'api_validity_period',
        'api_get_enable', 'api_jsonp_name'
    ]
    args = getArgs()

    path = getServerDir()
    opauth_cfg = path + '/config.json'
    content = mw.readFile(opauth_cfg)
    data = json.loads(content)

    for g in gets:
        if g in args:
            if g in ['cache_enable', 'redis_port',
                     'redis_db_index', 'api_validity_period', 'api_get_enable']:
                data[g] = int(args[g])
            else:
                data[g] = args[g]

    mw.writeFile(opauth_cfg, json.dumps(data))

    if os.path.exists(opauth_cfg):
        dst_conf = path + '/lua/opauth_conf.lua'
        data = mw.readFile(opauth_cfg)
        listToLuaFile(dst_conf, json.loads(data))

    restartWeb()
    return mw.returnJson(True, '设置成功')

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'install_pre_inspection':
        print(installPreInspection())
    elif func == 'redis_conf':
        print(getRedisConf())
    elif func == 'aes_conf':
        print(getAesConf())
    elif func == 'api_conf':
        print(getApiConf())
    elif func == 'submit_conf':
        print(submitConf())
    else:
        print('error')
