import sys,os
print(os.__file__)
print("python>>>>:",sys.argv[1],'XXXXXXXXX')
f = open('x.base64', 'r')
audiostr= f.readlines()[0].strip()
print(audiostr)
