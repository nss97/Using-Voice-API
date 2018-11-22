import io
import sys
import json
import hashlib
import base64
import time
import jieba

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

def convert_to_instruction(sentence):
    def deal_qiehuan(sentence):
        if sentence.count('模式'):
            return deal_moshi(sentence)
        elif sentence.count('主结构'):
            return deal_zhujiegou(sentence)
        elif sentence.count("配体"):
            return deal_peiti(sentence)
        elif sentence.count("拖") or sentence.count('拽'):
            return 71
        elif sentence.count("标签"):
            return 72
        return 0

    def deal_xianshi(sentence):
        if sentence.count('主') or sentence.count('结构'):
            return 29
        elif sentence.count('表') or sentence.count('面'):
            return 54
        elif sentence.count('配') or sentence.count('体'):
            return 36
        elif sentence.count('水') or sentence.count('分子'):
            return 41
        elif sentence.count('氢') or sentence.count('键'):
            return 43
        elif sentence.count('突') or sentence.count('变'):
            return 45
        return 0

    def deal_yincang(sentence):
        if sentence.count('主') or sentence.count('结构'):
            return 28
        elif sentence.count('表') or sentence.count('面'):
            return 53
        elif sentence.count('配') or sentence.count('体'):
            return 35
        elif sentence.count('水') or sentence.count('分子'):
            return 42
        elif sentence.count('氢') or sentence.count('键'):
            return 44
        elif sentence.count('突') or sentence.count('变'):
            return 46
        return 0

    def deal_biaomian(sentence):
        if sentence.count('透明'):
            return 51
        elif sentence.count('网格'):
            return 52
        elif sentence.count('隐藏'):
            return 53
        elif sentence.count('显示'):
            return 54
        return 0
    def deal_anzhao(sentence):
        if sentence.count('元素'):
            return 61
        elif sentence.count('氨基酸'):
            return 62
        elif sentence.count('二级') or sentence.count('结构'):
            return 63
        elif sentence.count('链'):
            return 64
        elif sentence.count('因') or sentence.count('子'):
            return 65
        elif sentence.count('谱'):
            return 66
        elif sentence.count('水') or sentence.count('疏'):
            return 67
        elif sentence.count('保守'):
            return 68
        return 0
    def deal_moshi(sentence):
        if sentence.count('桌面'):
            return 11
        elif sentence.count('虚拟') or sentence.count("现实"):
            return 12
        elif sentence.count('遨游'):
            return 13
        return 0
    def deal_zhujiegou(sentence):
        if sentence.count('线'):
            return 20
        elif sentence.count('点'):
            return 21
        elif sentence.count('链'):
            return 22
        elif sentence.count('球棍'):
            return 25
        elif sentence.count('球'):
            return 23
        elif sentence.count('棍'):
            return 24
        elif sentence.count('钢') or sentence.count('丝'):
            return 26
        elif sentence.count('二') or sentence.count('2'):
            return 27
        elif sentence.count('显示'):
            return 28
        elif sentence.count('隐藏'):
            return 29
        return 0

    def deal_peiti(sentence):
        if sentence.count('线'):
            return 31
        elif sentence.count('球棍'):
            return 34
        elif sentence.count('球'):
            return 32
        elif sentence.count('棍'):
            return 33
        elif sentence.count('显示'):
            return 35
        elif sentence.count('隐藏'):
            return 36
        return 0

    def deal_jiaohu(sentence,word_list):
        for word in word_list:
            if word=='拖拽':
                return 71
            elif word=='标签':
                return 72
            elif word=='旋转' or word=='转':
                return deal_zhuan(sentence)
            elif word=='动' or word=='移动':
                return deal_dong(sentence)
        return 0

    def deal_zhuan(sentence):
        if sentence.count('轴'):
            if sentence.count('横'):
                return 741
            elif sentence.count('纵'):
                return 742
            elif sentence.count('竖'):
                return 743
        elif sentence.count('顺'):
            return 75
        elif sentence.count('逆'):
            return 76
        return 73

    def deal_dong(sentence):
        return 0


    word_list = jieba.lcut(sentence)

    for word in word_list:
        if word=='切换':
            return deal_qiehuan(sentence)
        elif word=='显示':
            return deal_xianshi(sentence)
        elif word=='隐藏':
            return deal_yincang(sentence)
        elif word=='表面':
            return deal_biaomian(sentence)
        elif word=='按照':
            return deal_anzhao(sentence)
        elif word=='模式':
            return deal_moshi(sentence)
        elif word=='着色':
            return deal_anzhao(sentence)
        else:
            tmp=deal_jiaohu(sentence,word_list)
            if tmp!=0:
                return tmp

    return 0





# set for Chinese(只在php调用python脚本时使用，python单独运行时需注释掉)
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
language = sys.argv[1]

f = open('x.base64', 'r')
audiostr = f.readlines()[0].strip()

try:
    sentence = baidu_voice(audiostr)
    # out = jieba.lcut(sentence)
    baidu_result={'state':0, 'data':sentence}
except DemoError as err:
    # print("error: ",err.errorinfo)
    baidu_result = {'state': 1, 'error': err.errorinfo}


try:
    sentence = xunfei_voice(audiostr)
    # out = jieba.lcut(sentence)
    # convert_to_instruction(sentence)
    xunfei_result = {'state': 0, 'data': sentence}
except DemoError as err:
    # print("error: ",err.errorinfo)
    xunfei_result = {'state': 1, 'error': err.errorinfo}

print(json.dumps(baidu_result))
print(json.dumps(xunfei_result))

combine_sentence=""
if baidu_result['state']==0:
    combine_sentence+=baidu_result['data']
    combine_sentence+=','
if xunfei_result['state']==0:
    combine_sentence+=xunfei_result['data']
print(convert_to_instruction(combine_sentence))


