import torch
import os
import sys
from ReplayBuffer import ReplayBuffer
from memeory import Memory
from SumoAgent import SumoAgent
from genCar import GenCar
from agent import DQNAgent
from plots import mplot, record_data, IndSummaryPlot, IndSummaryPlot_S, record_data_2, IndSummaryPlot_S2
from fixedTime.ft_controller import ft_control, max_pressure
from dqn import dqn_control
import random
import time

MAX_EPOCH = 6
MAX_EPISODES = 30
MAX_STEPS = 7200

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

# 创建一个sumo agent
# 奖励的权重
c1, c2, c3 = 1, 0, 0
sumofile = './sumoNet/net.sumocfg'
port = 5905
inEdges = ['gneE1', 'gneE3', 'gneE0', 'gneE2']
outEdges = ['-gneE1', '-gneE3', '-gneE0', '-gneE2']

inLanes = ['gneE1_0', 'gneE1_1', 'gneE1_2',
           'gneE3_0', 'gneE3_1', 'gneE3_2',
           'gneE0_0', 'gneE0_1', 'gneE0_2',
           'gneE2_0', 'gneE2_1', 'gneE2_2']
outLanes = ['-gneE1_0', '-gneE1_1', '-gneE1_2',
            '-gneE3_0', '-gneE3_1', '-gneE3_2',
            '-gneE0_0', '-gneE0_1', '-gneE0_2',
            '-gneE2_0', '-gneE2_1', '-gneE2_2']
sumoAgent = SumoAgent(sumofile, port, inEdges, outEdges, inLanes, outLanes, sumoBinary='sumo-gui')

# 创建一个replayBuffer对象
capacity, minibatch = 30000, 2000
replayBuffer = ReplayBuffer(capacity, minibatch)
# memory = Memory(capacity,minibatch)

# 创建一个车辆生成器
# totalNumber, maxSteps, leftTurn, straight, scale = 4000, MAX_STEPS, 4, 4,  1
# gencar = GenCar(totalNumber, maxSteps, leftTurn, straight, fileName, scale)
# gencar.gen_dynamic_demand()
# gencar.generate_routefile()

# 初始化一个agent
in_dim, mid_dim, out_dim = 12, 3 * 9, 4
learning_rate, gamma, epsilon, alpha = 0.001, 0.95, 0.9, 0.3  # decay大概19轮左右
agent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent)

C = 3
net_update_times = 0
# dqn 数据记录
total_step_list, total_per_reward_list, total_per_queue_list, total_per_delay_list, total_per_travel_list = [], [], [], [], []


# 创建一个车辆生成器
totalNumber, maxSteps, leftTurn, straight, scale = 4000, MAX_STEPS, 4, 4, 1
# 生成50个数据集，以及对应的cfg文件
for i in range(50):
    path = "./sumoNet1/"
    fileName = "test{0}.rou.xml".format(i)
    gencar = GenCar(totalNumber, maxSteps, leftTurn, straight, path + fileName, scale)
    gencar.gen_dynamic_demand()
    gencar.generate_routefile()
    cfgFile = "net{0}.sumocfg".format(i)
    with open(path + cfgFile, 'w') as fp:
        print("""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="net.net.xml"/>
        <route-files value="{0}"/>

    </input>

    <time>
        <begin value="0"/>

        <step-length value="1"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
        <waiting-time-memory value="15"/>
    </processing>
    <gui_only>
        <start value="true"/>
        <quit-on-end value="true"/>
    </gui_only>

</configuration>
        """.format(fileName), file=fp)
print("数据集生成完成！")
l = [i for i in range(0, 50)]
for epoch in range(MAX_EPOCH):
    # print("===============================  epoch {0}  ===============================".format(epoch))
    # 随机选择30个路由文件
    choose = random.sample(l, MAX_EPISODES)
    queue_list, delay_list, travel_list, reward_list = [], [], [], []
    steps_list, per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []
    print("=========epoch {0} start time {1} ================".format(epoch, time.time()))
    for episode in range(MAX_EPISODES):
        sumofile = './sumoNet1/net{0}.sumocfg'.format(choose[episode])
        start_time = time.time()
        queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps = dqn_control(
            sumoAgent,
            sumofile, port,
            inEdges, outEdges,
            inLanes, outLanes,
            totalNumber,
            agent,
            MAX_EPISODES,
            MAX_STEPS, in_dim,
            net_update_times,
            C,
            replayBuffer)
        end_time = time.time()

        queue_list.append(queues)
        delay_list.append(delays)
        travel_list.append(travel_times)
        reward_list.append(rewards)
        per_reward_list.append(per_reward)
        per_queue_list.append(per_queue)
        per_delay_list.append(per_delay)
        per_travel_list.append(per_travel)
        steps_list.append(steps)

        print("episode={0} reward={1} steps={2} speed={3} elapsed={4}".format(episode, per_reward, steps, 0,
                                                                              start_time - end_time))
        # speed 没有计算

        # 每轮都记录一次数据 避免某次出现错误丧失数据！
        N = 101
        fname = 'data_save/data_{0}.xlsx'.format(N)
        data_list = {'rewards': reward_list,
                     'delay_time': delay_list,
                     'queue': queue_list,
                     'travel_time': travel_list,
                     'per_reward': per_reward_list,
                     'per_delay_time': per_delay_list,
                     'per_queue': per_queue_list,
                     'per_travel_time': per_travel_list}
        record_data(fname, data_list)

    total_per_reward_list.append(per_reward_list)
    total_per_queue_list.append(per_queue_list)
    total_per_delay_list.append(per_delay_list)
    total_per_travel_list.append(per_travel_list)
    total_step_list.append(steps_list)
N = 101

# 绘图
IndSummaryPlot_S(N, total_per_reward_list, 'per_reward')
IndSummaryPlot_S(N, total_per_queue_list, 'per_queue')
IndSummaryPlot_S(N, total_per_delay_list, 'per_delay')
IndSummaryPlot_S(N, total_per_travel_list, 'per_travel')
IndSummaryPlot_S(N, total_step_list, 'step')
# 将数据存入excel
fname = 'data_save/data_{0}.xlsx'.format(N)
data_list = {'step': total_step_list,
             'rewards': total_per_reward_list,
             'delay_time': total_per_delay_list,
             'queue': total_per_queue_list,
             'travel_time': total_per_travel_list,
             }
record_data_2(fname, data_list)

# 然后使用该模型进行测试 test
# 随机选取10个数据集
test_size = 10
choose = random.sample(l, test_size)
# dqn 数据记录
queue_list, delay_list, travel_list, reward_list = [], [], [], []
steps_list, per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []

# ft 数据记录
ft_queue_list, ft_delay_list, ft_travel_list = [], [], []
ft_steps, ft_per_queue_list, ft_per_travel_list, ft_per_delay_list = [], [], []

# mp 数据记录
mp_queue_list, mp_delay_list, mp_travel_list = [], [], []
mp_steps, mp_per_queue_list, mp_per_delay_list, mp_per_travel_list = [], [], []

for c in range(len(choose)):
    sumofile = './sumoNet1/net{0}.sumocfg'.format(choose[c])
    start_time = time.time()
    print("==========test {0} start time {1} ============".format(c, time.time()))
    ft_queues, ft_delays, ft_travels, ft_per_queue, ft_per_delay, ft_per_travel_time, ft_step = ft_control(sumoAgent,
                                                                                                           sumofile,
                                                                                                           port,
                                                                                                           inEdges,
                                                                                                           outEdges,
                                                                                                           inLanes,
                                                                                                           outLanes,
                                                                                                           totalNumber,
                                                                                                           MAX_STEPS)
    ft_queue_list.append(ft_queues)
    ft_delay_list.append(ft_delays)
    ft_travel_list.append(ft_travels)
    ft_per_queue_list.append(ft_per_queue)
    ft_per_delay_list.append(ft_per_delay)
    ft_per_travel_list.append(ft_per_travel_time)
    ft_steps.append(ft_step)
    print('ft finished')
    # mp_sumofile = './sumoNet/net2.sumocfg'
    # mp_queues, mp_delays, mp_travels, mp_per_queue, mp_per_delay, mp_per_travel_time,mp_step = max_pressure(sumoAgent,
    #                                                                                                 mp_sumofile, port,
    #                                                                                                 inEdges,
    #                                                                                                 outEdges, inLanes,
    #                                                                                                 outLanes,
    #                                                                                                 totalNumber,
    #                                                                                                 MAX_STEPS)
    # mp_queue_list.append(mp_queues)
    # mp_delay_list.append(mp_delays)
    # mp_travel_list.append(mp_travels)
    # mp_per_queue_list.append(mp_per_queue)
    # mp_per_delay_list.append(mp_per_delay)
    # mp_per_travel_list.append(mp_per_travel_time)
    # mp_steps.append(mp_step)
    # print("mp finished")
    queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps = dqn_control(sumoAgent,
                                                                                                             sumofile,
                                                                                                             port,
                                                                                                             inEdges,
                                                                                                             outEdges,
                                                                                                             inLanes,
                                                                                                             outLanes,
                                                                                                             totalNumber,
                                                                                                             agent,
                                                                                                             MAX_EPISODES,
                                                                                                             MAX_STEPS,
                                                                                                             in_dim,
                                                                                                             net_update_times,
                                                                                                             C,
                                                                                                             replayBuffer)
    end_time = time.time()

    queue_list.append(queues)
    delay_list.append(delays)
    travel_list.append(travel_times)
    reward_list.append(rewards)
    per_reward_list.append(per_reward)
    per_queue_list.append(per_queue)
    per_delay_list.append(per_delay)
    per_travel_list.append(per_travel)
    steps_list.append(steps)

# 绘制图形

IndSummaryPlot_S2(N, 'per_reward', dqn=per_reward_list)
IndSummaryPlot_S2(N, 'per_queue', ft=ft_per_queue_list, mp=mp_queue_list, dqn=per_queue_list)
IndSummaryPlot_S2(N, 'per_delay', ft=ft_per_delay_list, mp=mp_per_delay_list, dqn=per_delay_list)
IndSummaryPlot_S2(N, 'per_travel', ft=ft_per_travel_list, mp=mp_per_travel_list, dqn=per_travel_list)
IndSummaryPlot_S2(N, 'step', ft=ft_steps, mp=mp_steps, dqn=steps_list)

fname2 = 'data_save/ft_data_{0}.xlsx'.format(N)
data_list2 = {'ft_delay_time': ft_delay_list,
              'ft_queue': ft_queue_list,
              'ft_travel_time': ft_travel_list,
              'ft_per_delay_time': ft_per_delay_list,
              'ft_per_queue': ft_per_queue_list,
              'ft_per_travel_time': ft_per_travel_list,
              'ft_steps':ft_steps
              }
record_data(fname2, data_list2)

fname3 = 'data_save/mp_data_{0}.xlsx'.format(N)
data_list3 = {'mp_delay_time': mp_delay_list,
              'mp_queue': mp_queue_list,
              'mp_travel_time': mp_travel_list,
              'mp_per_delay_time': mp_per_delay_list,
              'mp_per_queue': mp_per_queue_list,
              'mp_per_travel_time': mp_per_travel_list,
              'mp_steps': mp_steps
              }
record_data(fname3, data_list3)

fname4 = 'data_save/dqn_test_data_{0}.xlsx'.format(N)
data_list4 = {'rewards': reward_list,
             'delay_time': delay_list,
             'queue': queue_list,
             'travel_time': travel_list,
             'per_reward': per_reward_list,
             'per_delay_time': per_delay_list,
             'per_queue': per_queue_list,
             'per_travel_time': per_travel_list,
             'steps': steps_list
              }
record_data(fname4, data_list4)
