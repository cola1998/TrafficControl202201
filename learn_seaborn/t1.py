import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns; sns.set()    # 设置美化参数，一般默认就好
import pandas as pd

# rewards = np.array([0,0.1,0,0.2,0.4,0.5,0.6,0.9,0.9,0.9])
# sns.lineplot(x=range(len(rewards)), y=rewards)
# # sns.relplot(x=range(len(rewards)),y=rewards,kind='line') # 等价于上一行
# plt.xlabel('episode')
# plt.ylabel('reward')
# plt.show()

'''
实际上实际部分是seaborn默认对同一x轴的多个y值即rewards做了均值，阴影部分表示多组rewards的范围，可以使用sns.lineplot(x=episode,y=rewards,ci=None)去掉。
'''
# rewards1 = np.array([0, 0.1,0,0.2,0.4,0.5,0.6,0.9,0.9,0.9])
# rewards2 = np.array([0, 0,0.1,0.4,0.5,0.5,0.55,0.8,0.9,1])
# rewards=np.concatenate((rewards1,rewards2)) # 合并数组
# episode1=range(len(rewards1))
# episode2=range(len(rewards2))
# episode=np.concatenate((episode1,episode2))
# sns.lineplot(x=episode,y=rewards)
# plt.xlabel("episode")
# plt.ylabel("reward")
# plt.show()

# 使用pandas传数据

# rewards1 = np.array([0, 0.1,0,0.2,0.4,0.5,0.6,0.9,0.9,0.9])
# rewards2 = np.array([0, 0,0.1,0.4,0.5,0.5,0.55,0.8,0.9,1])
# rewards = np.vstack((rewards1,rewards2))  # 合并数组
# df = pd.DataFrame(rewards).melt(var_name='episode', value_name='reward') # 推荐这种转换方式
# # melt 将所有维合并成一列
# '''
# episode  reward
# 0      0  0.0
# 1      0  0.1
# 2      0  0.2
# 3      0  0.4
# 4      0  0.9
# '''
# sns.lineplot(x='episode',y='reward',data=df)  # 这里的x，y不再传入数组，而是对应dataFrame中的列名
# plt.show()


# 一种更适合paper的绘制方式
def get_data():
    basecond = np.array([[18, 20, 19, 18, 13, 4, 1],[20, 17, 12, 9, 3, 0, 0],[20, 20, 20, 12, 5, 3, 0]])
    cond1 = np.array([[18, 19, 18, 19, 20, 15, 14],[19, 20, 18, 16, 20, 15, 9],[19, 20, 20, 20, 17, 10, 0]])
    cond2 = np.array([[20, 20, 20, 20, 19, 17, 4],[20, 20, 20, 20, 20, 19, 7],[19, 20, 20, 19, 19, 15, 2]])
    cond3 = np.array([[20, 20, 20, 20, 19, 17, 12],[18, 20, 19, 18, 13, 4, 1], [20, 19, 18, 17, 13, 2, 0]])
    return basecond, cond1, cond2, cond3

data = get_data()
print(data)
label = ['algo1','algo2','algo3','algo4']
df = []
for i in range(len(data)):
    df.append(pd.DataFrame(data[i]).melt(var_name='episode',value_name='loss'))
    df[i]['algo'] = label[i]
print("0/n",df)
df = pd.concat(df)
print("1/n",df)
sns.lineplot(x='episode', y='loss', hue='algo', style='algo', data=df)
plt.title('some loss')
plt.show()