import io
import sys
import json
import hashlib
import base64
import time

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode


class DemoError(Exception):
    # pass
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo

def baidu_voice(audio):
    # flags
    API_KEY = 'NgawfS7s6NzVeFreXyYHWU6H'
    SECRET_KEY = 'uvdyW57F7gCa817kmut4MGo9LTaPHBZw'
    FORMAT = 'wav';  # 文件格式：文件后缀只支持 pcm/wav/amr
    DEV_PID = 1536;  # 根据文档填写PID，选择语言及识别模型：1536表示识别普通话，使用搜索模型.1737 english
    CUID = '123456jwefjoefjoej';
    RATE = 16000;  # 采样率：固定值
    ASR_URL = 'http://vop.baidu.com/server_api'
    TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
    SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选

    def fetch_token():
        # 生成token请求
        params = {'grant_type': 'client_credentials', 'client_id': API_KEY, 'client_secret': SECRET_KEY}
        post_data = urlencode(params)
        post_data = post_data.encode('utf-8')

        # 请求token
        req = Request(TOKEN_URL, post_data)

        # 处理结果，提取access_token
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            # print('token http response http code : ' + str(err.code))
            raise DemoError("Cannot get token from baidu, response error" + str(err.code))
        result_str = result_str.decode()
        result = json.loads(result_str)
        if ('access_token' in result.keys() and 'scope' in result.keys()):
            # if not SCOPE in result['scope'].split(' '):
            #     raise DemoError('scope is not correct')
            # print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
            return result['access_token']
        else:
            raise DemoError(
                'MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    def convert(token, audio):
        length = len(base64.urlsafe_b64decode(audio))
        params = {'dev_pid': DEV_PID,
                  'format': FORMAT,
                  'rate': RATE,
                  'token': token,
                  'cuid': CUID,
                  'channel': 1,
                  'speech': audio,
                  'len': length,
                  }
        post_data = json.dumps(params, sort_keys=False)
        # print post_data
        req = Request(ASR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')

        # 判断是否翻译成功，取出文本
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('asr http response http code : ' + str(err.code))
            raise DemoError("Cannot get asr from baidu, response error" + str(err.code))
        result_str = str(result_str, 'utf-8')
        result = json.loads(result_str)

        # print(result)
        if ('result' in result.keys()):
            return result['result'][0]
        else:
            # print(result)
            raise DemoError(result)

    token = fetch_token()
    return convert(token, audio)


def xunfei_voice(audio):
    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = '905183e09e5f792c4cdf4e24cf8a8a4d'  # api key在这里
    x_appid = '5be15d7d'  # appid在这里
    param = {"engine_type": "sms16k", "aue": "raw"}  # 普通话(sms16k),普通话(sms8k),英语(sms-en8k),英语(sms-en16k)
    x_time = int(int(round(time.time() * 1000)) / 1000)

    # get checksum
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_checksum_content = api_key + str(x_time) + str(x_param, 'utf-8')
    x_checksum = hashlib.md5(x_checksum_content.encode('utf-8')).hexdigest()

    body = urlencode({'audio': audio})
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}

    req = Request(url=url, data=body.encode('utf-8'), headers=x_header, method='POST')

    try:
        result = urlopen(req)
        result = result.read().decode('utf-8')
    except URLError as err:
        raise DemoError("Cannot get asr from xunfei, response error" + str(err.code))

    result = json.loads(result)
    # print(result)
    if ('data' in result.keys()):
        return result['data']
    else:
        raise DemoError(result)


# set for Chinese(只在php调用python脚本时使用，python单独运行时需注释掉)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
language = sys.argv[1]

f = open('x.base64', 'r')
audiostr = f.readlines()[0].strip()

try:
    tmp = baidu_voice(audiostr)
    print("data: ",tmp)
except DemoError as err:
    print("error: ",err.errorinfo)

try:
    tmp = xunfei_voice(audiostr)
    print("data: ",tmp)
except DemoError as err:
    print("error: ",err.errorinfo)

