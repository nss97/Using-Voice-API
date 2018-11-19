#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib.parse, urllib.request
import time
import json
import hashlib
import base64

def main():
    f = open("record2.wav", 'rb')
    # rb表示以二进制格式只读打开文件

    file_content = f.read()
    # file_content 是二进制内容，bytes类型
    # 由于Python的字符串类型是str，在内存中以Unicode表示，一个字符对应若干个字节。
    # 如果要在网络上传输，或者保存到磁盘上，就需要把str变为以字节为单位的bytes
    base64_audio = base64.b64encode(file_content)
    # base64.b64encode()参数是bytes类型，返回也是bytes类型

    body = urllib.parse.urlencode({'audio': base64_audio})
    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = '905183e09e5f792c4cdf4e24cf8a8a4d'  # api key在这里
    x_appid = '5be15d7d'  # appid在这里
    param = {"engine_type": "sms-en16k", "aue": "raw"} # 普通话(sms16k),普通话(sms8k),英语(sms-en8k),英语(sms-en16k)

    x_time = int(int(round(time.time() * 1000)) / 1000)

    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    # 这是3.x的用法，因为3.x中字符都为unicode编码，而b64encode函数的参数为byte类型，
    # 所以必须先转码为utf-8的bytes
    # >> print(x_param)
    # >> b'YWJjcjM0cjM0NHI ='
    # 结果和我们预想的有点区别，我们只想要获得YWJjcjM0cjM0NHI =，而字符串被b
    # ''包围了。这时肯定有人说了，用正则取出来就好了。。。别急。b表示
    # byte的意思，我们只要再将byte转换回去就好了:
    # >> x_param = str(x_param, 'utf-8')
    x_checksum_content = api_key + str(x_time) + str(x_param, 'utf-8')
    x_checksum = hashlib.md5(x_checksum_content.encode('utf-8')).hexdigest()

    # python3里的hashlib.md5()参数也是要求bytes类型的，x_checksum_content是以Unicode编码的，所以需要转成bytes。
    # 讯飞api说明：
    # 授权认证，调用接口需要将Appid，CurTime, Param和CheckSum信息放在HTTP请求头中；
    # 接口统一为UTF-8编码；
    # 接口支持http和https；
    # 请求方式为POST。
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}

    req = urllib.request.Request(url=url, data=body.encode('utf-8'), headers=x_header, method='POST')

    result = urllib.request.urlopen(req)
    result = result.read().decode('utf-8')

    # print(result)
    result = json.loads(result)
    if ('data' in result.keys()):
        # if not SCOPE in result['scope'].split(' '):
        #     raise DemoError('scope is not correct')
        # print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['data']
    else:
        print(result['desc'])
    return


if __name__ == '__main__':
    result=main()
    print(result)

# {"code":"10105",
#  "data":"",
#  "desc":"illegal access|illegal client_ip: 58.248.139.205",
#  "sid":"zat00051e0e@ch26260e3773f83d3400"}
# 我讯飞后台需要开ip白名单