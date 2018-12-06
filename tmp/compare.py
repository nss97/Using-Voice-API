def cal_score(sentence, command):
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
        score_1 = lcs_i / max(len(i[0]), len(sentence))
        score_2 = 2 * lcs_i / (len(i[0]) + len(sentence))
        score_3 = lcs_i / (len(i[0]) + len(sentence) - lcs_i)

        common_character = set(i[0]).intersection(set(sentence))
        score_4 = len(common_character) / (len(i[0]) + len(sentence) - len(common_character))

        command_name = i[1]
        command_score[command_name] = [score_1, score_2, score_3, score_4]

    return [find_max(command_score, 0),
            find_max(command_score, 1),
            find_max(command_score, 2),
            find_max(command_score, 3)]


csv_file = csv.reader(open('command.csv'))
command = []
for i in csv_file:
    command.append(i)

csv_file = csv.reader(open('result.csv'))
result = []
for i in csv_file:
    result.append(i)

output = []
for i in result:
    answer = i[0]
    v = i[1]
    out = [answer, v]
    baidu = cal_score(i[2], command)
    for j in baidu:
        if j[1] == answer:
            out.append(1)
        else:
            out.append(0)

    xunfei = cal_score(i[3], command)
    for j in xunfei:
        if j[1] == answer:
            out.append(1)
        else:
            out.append(0)

    output.append(out)

import pandas

data = pandas.DataFrame(output,
                        columns={'id', 'v', 'baidu1', 'baidu2', 'baidu3', 'baidu4', 'xunfei1', 'xunfei2', 'xunfei3',
                                 'xunfei4'})
data.to_csv('judge_right_or_wrong.csv')
