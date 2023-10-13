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
```
