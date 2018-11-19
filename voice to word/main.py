import json
import base64
import time

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
timer = time.perf_counter

API_KEY = 'NgawfS7s6NzVeFreXyYHWU6H'
SECRET_KEY = 'uvdyW57F7gCa817kmut4MGo9LTaPHBZw'

# 需要识别的文件
AUDIO_FILE = 'record.wav' # 只支持 pcm/wav/amr
# 文件格式
FORMAT = 'wav';  # 文件后缀只支持 pcm/wav/amr

# 根据文档填写PID，选择语言及识别模型
DEV_PID = 1536;  #1536表示识别普通话，使用搜索模型.1737 english

CUID = '123456jwefjoefjoej';
# 采样率
RATE = 16000;  # 固定值

ASR_URL = 'http://vop.baidu.com/server_api'

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选

class DemoError(Exception):
    pass

def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode( 'utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str =  result_str.decode()

    # print(result_str)
    result = json.loads(result_str)
    # print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

def convert(token):
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()
    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)
    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        f = urlopen(req)
        result_str = f.read()
    except  URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()

    result_str = str(result_str, 'utf-8')
    result = json.loads(result_str)

    if ('result' in result.keys()):
        # if not SCOPE in result['scope'].split(' '):
        #     raise DemoError('scope is not correct')
        # print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['result']
    else:
        print(result['err_msg'])
        raise DemoError('MAYBE input not correct: access_token or scope not found in token response')

if __name__ == '__main__':
    token = fetch_token()
    result = convert(token)
    print(result)



