import sys
import json
import hashlib
import base64
import csv
import io
import time
import re

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode


class DemoError(Exception):
    # pass
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo


def baidu_voice(audio, language):
    FORMAT = 'wav';  # 文件格式：文件后缀只支持 pcm/wav/amr
    DEV_PID = 1536;  # 根据文档填写PID，选择语言及识别模型：1536表示识别普通话，使用搜索模型.1737 english
    CUID = '123456jwefjoefjoej';
    RATE = 16000;  # 采样率：固定值
    ASR_URL = 'http://vop.baidu.com/server_api'

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

    with open('util/token.txt', 'r') as f:
        token = f.read()
    # print(token)
    result = convert(token, audio)
    return result


def xunfei_voice(audio, language):
    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = '905183e09e5f792c4cdf4e24cf8a8a4d'  # api key在这里
    x_appid = '5be15d7d'  # appid在这里
    if language == 'Chinese' or language == 'chinese':
        lang = "sms16k"
    else:
        lang = "sms-en16k"
    param = {"engine_type": lang, "aue": "raw"}  # 普通话(sms16k),普通话(sms8k),英语(sms-en8k),英语(sms-en16k)
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
        # print(err)
        raise DemoError("Cannot get asr from xunfei, response error" + str(err.code))

    result = json.loads(result)
    # print("nanana",result)
    if (result['desc'] == 'success'):
        return result['data']
    else:
        raise DemoError(result)


def convert_chinese_to_instruction(sentence, command):
    def lcs(s1, s2):
        l1 = len(s1)
        l2 = len(s2)
        if l1 <= 0 or l2 <= 0:
            return 0
        dp = [[0] * (l2 + 1) for j in range(l1 + 1)]
        for i in range(1, l1 + 1):
            for j in range(1, l2 + 1):
                if (s1[i - 1] == s2[j - 1]):
                    dp[i][j] = 1 + dp[i - 1][j - 1]
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[l1][l2]

    def find_max(command_score, index):
        maxm = 0
        id = '0'
        for i in command_score.keys():
            if command_score[i][index] > maxm:
                maxm = command_score[i][index]
                id = i
        if maxm >= 0.2:
            return (maxm, id)
        else:
            return (1, '0')

    command_score = {}
    for i in command:
        lcs_i = lcs(i[0], sentence)
        command_name = i[1]

        #     score_1 = lcs_i / max(len(i[0]), len(sentence))
        #     score_2 = 2 * lcs_i / (len(i[0]) + len(sentence))
        #     score_3 = lcs_i / (len(i[0]) + len(sentence) - lcs_i)
        #
        #     common_character = set(i[0]).intersection(set(sentence))
        #     score_4 = len(common_character) / (len(i[0]) + len(sentence) - len(common_character))
        #
        #     command_score[command_name] = [score_1, score_2, score_3, score_4]
        #
        # return {1: find_max(command_score, 0),
        #         2: find_max(command_score, 1),
        #         3: find_max(command_score, 2),
        #         4: find_max(command_score, 3)}

        score = lcs_i / max(len(i[0]), len(sentence))
        command_score[command_name] = score
        max_score = max(zip(command_score.values(), command_score.keys()))
        if max_score[0] >= 0.2:
            return max_score
        else:
            return (1, '0')


def convert_english_to_instruction(sentence):
    return 0


# set for Chinese(只在php调用python脚本时使用，python单独运行时需注释掉)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
language = sys.argv[1]
file_name = sys.argv[2]
f = open('base64/' + file_name, 'r')
audiostr = f.readlines()[0].strip()

csv_file = csv.reader(open('command.csv'))
command = []
for i in csv_file:
    command.append(i)

try:
    sentence = baidu_voice(audiostr, language)
    # out = jieba.lcut(sentence)
    score = convert_chinese_to_instruction(sentence, command)
    baidu_result = {'state': 0, 'data': sentence, 'score': score}
except DemoError as err:
    # print("error: ",err.errorinfo)
    baidu_result = {'state': 1, 'error': err.errorinfo}

try:
    sentence = xunfei_voice(audiostr, language)
    sentence = re.sub("[！，。？]", "", sentence)  # 去除标点
    score = convert_chinese_to_instruction(sentence, command)
    xunfei_result = {'state': 0, 'data': sentence, 'score': score}
except DemoError as err:
    xunfei_result = {'state': 1, 'error': err.errorinfo}

print(json.dumps(baidu_result))
print(json.dumps(xunfei_result))
print(0)  # 确定的操作值

# if language=="Chinese" or language=='chinese':
#     print()
# else:
#     # convert_english_to_instruction(combine_sentence)
#     print(combine_sentence)
