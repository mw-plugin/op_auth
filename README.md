# OP鉴权

OP鉴权-基于OpenResty文件访问鉴权

# 一键安装
```
cd /www/server/mdserver-web/plugins && rm -rf op_auth && git clone https://github.com/mw-plugin/op_auth && cd op_auth && rm -rf .git && cd /www/server/mdserver-web/plugins/op_auth && bash install.sh install 1.0
```

# PHP 使用例子
```
<?php
class AES
{
    private $key;
    private $iv;

    public function __construct($key, $iv)
    {
        $this->key = $key;
        $this->iv = $iv;
    }

    /**
     * 发起POST请求
     * @param String $url 目标网填，带http://
     * @param Array|String $data 欲提交的数据
     * @return string
     */
    private function post($url, $data, $timeout = 60)
    {

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $output = curl_exec($ch);
        curl_close($ch);
        return $output;
    }

    public function encrypt($data)
    {
        $encrypted = openssl_encrypt($data, 'AES-128-ECB', $this->key, OPENSSL_RAW_DATA);
        return base64_encode($encrypted);
    }

    public function decrypt($encryptedData)
    {
        $decrypted = openssl_decrypt(base64_decode($encryptedData), 'AES-128-ECB', $this->key, OPENSSL_RAW_DATA);
        return $decrypted;
    }

    public function encryptCBC($data)
    {
        $encrypted = openssl_encrypt($data, 'AES-256-CBC', $this->key, OPENSSL_RAW_DATA, $this->iv);
        return base64_encode($encrypted);
    }

    public function decryptCBC($encryptedData)
    {
        $decrypted = openssl_decrypt(base64_decode($encryptedData), 'AES-256-CBC', $this->key, OPENSSL_RAW_DATA, $this->iv);
        return $decrypted;
    }

    public function getToken($url)
    {
        return $this->post($url, []);
    }
}
// 使用示例：
$key = 'fGriF7gbvDVyY2Jw'; // 16字节长度的密钥
$iv = 'lzcwYnaS27lxgR8p'; // 16字节长度的初始向量
$aes = new AES($key, $iv);

$data = $aes->getToken('http://127.0.0.1:7879/opauth_get_token');
$data = json_decode($data, true);

echo ($data['msg'] . "<br/>");
$dedata = $aes->decrypt($data['msg']);
echo ($dedata . "<br/>");

echo ('http://127.0.0.1:7879/?token=' . $dedata . "<br/>");
```

# Python 使用例子
```
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

```
