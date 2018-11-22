instructions=['旋转','平移', '选择', '放大']

sentences=['切换主结构为主链风格', '切换为虚拟现实模式','切换为遨游模式']

import jieba

out=jieba.lcut(sentences[0])

print(out)

out=jieba.lcut(sentences[1])

print(out)

out=jieba.lcut(sentences[2])

print(out)