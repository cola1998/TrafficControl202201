import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter
import seaborn as sns;

sns.set()
import pandas as pd


def mplot(y, title, N):
    x = np.arange(1, len(y) + 1)
    plt.plot(x, y)
    plt.title(title)
    plt.savefig('data_save/' + title + '_{0}.png'.format(N))
    plt.show()


def IndSummaryPlot(N, *args, **kwargs):
    '''

    :param N: 图片标号
    :param args: 传入 1,2,3  接收为元组 (1,2,3)
    :param kwargs: 传入 index1=22,index2=33 接收为字典 {'index1':22,'index2':33}
    :return:
    '''
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # args 传入指标顺序  queues,delays,travel_times  三个指标
    # kwargs 算法为key  指标list为值   ft,mp,dqn  多种算法
    a = list(kwargs.keys())  # 图例list
    values = [[] for i in range(len(args))]
    print(kwargs)
    for k in a:
        for i in range(len(kwargs[k])):
            values[i].append(kwargs[k][i])

    print(values)

    colorD = {'ft': '#4e72b8', 'mp': '#8552a1', 'dqn': 'r'}
    x = np.arange(1, len(kwargs[a[0]][0]) + 1)
    print(x)

    plt.figure(figsize=(10, 10), dpi=80)
    plt.figure("汇总")

    ax1 = plt.subplot(311)  # 3行1列 取第一块

    for i in range(len(values[0])):
        ax1.plot(x, values[0][i], color=colorD[a[i]], label=a[i], linewidth=1 if a[i] != 'dqn' else 3)
    ax1.legend()
    ax1.set_title(args[0])
    ax1.set_xlabel("episodes")
    ax1.set_ylabel(args[0])

    ax2 = plt.subplot(312)  # 3行1列 取第一块
    for i in range(len(values[1])):
        ax2.plot(x, values[1][i], color=colorD[a[i]], label=a[i], linewidth=1 if a[i] != 'dqn' else 3)
    ax2.legend()
    ax2.set_title(args[1])
    ax2.set_xlabel("episodes")
    ax2.set_ylabel(args[1])

    ax3 = plt.subplot(313)  # 3行1列 取第一块
    for i in range(len(values[2])):
        ax3.plot(x, values[2][i], color=colorD[a[i]], label=a[i], linewidth=1 if a[i] != 'dqn' else 3)
    ax3.legend()
    ax3.set_title(args[2])
    ax3.set_xlabel("episodes")
    ax3.set_ylabel(args[2])

    # my_x_ticks = np.arange(1, 14, 1)  # !控制横坐标网格化程度，显示更加美观
    # plt.xticks(my_x_ticks)
    plt.savefig('data_save/Summary_{0}.png'.format(N))
    plt.show()


def IndSummaryPlot_S(N, data, key):
    '''

    :param N: 图片标号
    :param data: 传入数据
    :param key: 指标名称
    :return:
    '''
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # args 传入指标顺序
    # kwargs 指标为key {queues,delays,travel_times  三个指标}
    data = np.array(data)
    df = pd.DataFrame(data).melt(var_name='episode', value_name=key)
    sns.lineplot(x='episode', y=key, data=df)
    plt.savefig('data_save/sns_{0}_{1}.png'.format(key, N))
    plt.show()


def IndSummaryPlot_S2(N, index, **kwargs):
    '''

    :param N: 图片标号
    :param data: 传入数据
    :param key: 指标名称
    :return:
    '''
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # args 传入指标顺序
    # kwargs 指标为key {queues,delays,travel_times  三个指标}
    keys = list(kwargs.keys())
    df = []
    for i in range(len(keys)):
        df.append(pd.DataFrame(np.array(kwargs[keys[i]])).melt(var_name='episode', value_name=index))
        df[i]['algo'] = keys[i]
    print(df)
    df = pd.concat((df))
    sns.lineplot(x='episode', y=index,hue='algo',style='algo',data=df)
    plt.savefig('data_save/sns_{0}_{1}.png'.format(index, N))
    plt.show()


def record_data(file_name, d):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    name_list = list(d.keys())
    for j in range(len(name_list)):
        worksheet.write(0, j, name_list[j])

    for i in range(len(d[name_list[0]])):  # i 代表行 j代表列
        for j in range(len(name_list)):
            worksheet.write(i + 1, j, d[name_list[j]][i])

    workbook.close()


def record_data_2(file_name, d):
    name_list = list(d.keys())
    df = []
    for i in range(len(name_list)):
        key = name_list[i]
        IndSummaryPlot_S(100, d[key], key)
        df.append(pd.DataFrame(np.array(d[key])).melt(var_name='episode', value_name=key))
    df = pd.concat(df)
    # print(df)
    df.to_excel(file_name)


# if __name__ == '__main__':
#     fname = 'data_save/data_{0}.xlsx'.format(N)
#     N = 1
#     data_list = {'reward': reward_list,
#                  'delay_time': delay_list,
#                  'queue': queue_list, }
#     record_data(fname, data_list)

def boxPlot(title):
    # https://www.jianshu.com/p/0576b417bfcd
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    df = pd.DataFrame(data)
    df.plot.box(title=title)
    plt.grid(linestyle='--', alpha=0.3)
    plt.show()


if __name__ == '__main__':
    # boxPlot('123')
    # IndSummaryPlot(10,'queue','delay','travel_time',ft=[[1,2,2,4],[1,2,2,4],[1,2,2,4]],dqn=[[1,3,2,2],[1,3,2,2],[1,3,2,2]],mp=[[1.5,3,1,4],[1.5,3,1,4],[1.5,3,1,4]])
    # reward_list = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]]
    # delay_list = [[11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25]]
    # queue_list = [[31, 32, 33, 34, 35], [36, 37, 38, 39, 40], [41, 42, 43, 44, 45]]
    # data_list = {'reward': reward_list,
    #              'delay_time': delay_list,
    #              'queue': queue_list, }
    # record_data_2('data_save/1.xlsx', data_list)
    IndSummaryPlot_S2(1000,'queue',ft=[[1,2,2,4],[2,4,6,7],[0,2,9,9]],dqn=[[1,3,2,2],[1,3,2,2],[1,3,2,2]],mp=[[1.5,3,1,4],[1.5,3,1,4],[1.5,3,1,4]])
