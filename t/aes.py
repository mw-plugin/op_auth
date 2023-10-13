# coding:utf-8

import base64
import json
# pip install pycrypto
# pip install pycryptodomex
from Cryptodome.Cipher import AES


# 密钥（key）, 密斯偏移量（iv） CBC模式加密


def httpGet(url, timeout=30):
    import urllib.request
    try:
        import ssl
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
        req = urllib.request.urlopen(url, timeout=timeout)
        result = req.read().decode('utf-8')
        return result

    except Exception as e:
        return str(e)


def AES_Encrypt(key, data):
    vi = '0102030405060708'
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    data = pad(data)
    # 字符串补位
    cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    encryptedbytes = cipher.encrypt(data.encode('utf8'))
    # 加密后得到的是bytes类型的数据
    encodestrs = base64.b64encode(encryptedbytes)
    # 使用Base64进行编码,返回byte字符串
    enctext = encodestrs.decode('utf8')
    # 对byte字符串按utf-8进行解码
    return enctext


def AES_Decrypt(key, data):
    vi = 'lzcwYnaS27lxgR8p'
    data = data.encode('utf8')
    encodebytes = base64.decodebytes(data)
    # 将加密数据转换位bytes类型数据
    cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    text_decrypted = cipher.decrypt(encodebytes)
    # unpad = lambda s: s[0:-s[-1]]
    # text_decrypted = unpad(text_decrypted)
    # 去补位
    text_decrypted = text_decrypted.decode('utf8')
    return text_decrypted


key = 'fGriF7gbvDVyY2Jw'  # 自己密钥

data = httpGet('http://127.0.0.1:7879/opauth_get_token')
data = json.loads(data)
print(data)
text_decrypted = AES_Decrypt(key, data['msg'])
print(text_decrypted)

print('http://127.0.0.1:7879/?token=' + text_decrypted)
