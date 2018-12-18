import pandas
# import matplotlib.pyplot as plt


data=pandas.read_csv("judge_right_or_wrong.csv")
# data.plot()
mean_t=data.groupby(['v']).mean()
mean_t.to_csv("ans.csv")