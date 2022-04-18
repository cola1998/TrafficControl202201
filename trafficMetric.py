import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 绘制好看的图像参考链接 https://www.machinelearningplus.com/plots/top-50-matplotlib-visualizations-the-master-plots-python/
# 添加图例参考链接 https://queirozf.com/entries/matplotlib-examples-displaying-and-configuring-legends
'''
sumolight中绘图
1. standard deviation travel time[标准差旅行时间] mean travel time
'''

class TrafficMetric:
    def __init__(self):
        # 用于存储啥的吧 将数据写入文件 绘图等等
        pass
    # 一个是delay_time 一个是queue 用这两个指标评估不同模型之间的差异
    # 使用travel time来评估模型超参数
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文内容
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
def plotMultiP():
    t = np.arange(0.0, 2.0, 0.1)
    s = np.sin(t * np.pi)

    plt.figure(figsize=(8,8),dpi=80)
    plt.figure(1)  # 去第一块画板
    ax1 = plt.subplot(311) # 分成三行一列 取第一块
    ax1.plot(t,s,color='r',linestyle='-')
    ax2 = plt.subplot(312)
    ax2.plot(t, s, color='y', linestyle='-')
    ax3 = plt.subplot(313)
    ax3.plot(t, s, color='g', linestyle='-')
    plt.show()
plotMultiP()