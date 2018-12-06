import base64

name="../base64/1206141541_75.base64"
file="voice.wav"

with open(name, 'r') as fileObj:
    base64_data = fileObj.read()
    ori_data = base64.b64decode(base64_data)
    # print(ori_data)
    fout = open(file, 'wb')
    fout.write(ori_data)
    fout.close()
