import torch
import os
import sys
from ReplayBuffer import ReplayBuffer
from memeory import Memory
from SumoAgent import SumoAgent
from genCar1 import GenCar
from agent import DQNAgent
from plots import record_data, IndSummaryPlot_S, record_data_2, IndSummaryPlot_S2
from fixedTime.ft_controller import ft_control, max_pressure
from dqn import dqn_control_norm,dqn_control_norm2
import numpy as np
import random
import time
from tensorboardX import SummaryWriter

MAX_EPOCHS = 3
MAX_EPISODES = 100
MAX_STEPS = 3600
SAMPLE_SIZES = int(MAX_EPISODES * 1.5)

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

# 创建一个sumo agent
# 奖励的权重
c1, c2, c3 = 1, 0, 0
sumofile = './sumoNet3/net.sumocfg'
port = 5905

inEdges = ['road_0_1_0', 'road_2_1_2', 'road_1_0_1', 'road_1_2_3']
outEdges = ['road_1_1_0', 'road_1_1_2', 'road_1_1_1', 'road_1_1_3']
inLanes = ['road_0_1_0_2', 'road_0_1_0_1', 'road_0_1_0_0',
           'road_2_1_2_2', 'road_2_1_2_1', 'road_2_1_2_0',
           'road_1_0_1_2', 'road_1_0_1_1', 'road_1_0_1_0',
           'road_1_2_3_2', 'road_1_2_3_1', 'road_1_2_3_0']
outLanes = ['road_1_1_0_2', 'road_1_1_0_1', 'road_1_1_0_0',
            'road_1_1_2_2', 'road_1_1_2_1', 'road_1_1_2_0',
            'road_1_1_1_2', 'road_1_1_1_1', 'road_1_1_1_0',
            'road_1_1_3_2', 'road_1_1_3_1', 'road_1_1_3-0']
I = {'w': 'road_0_1_0', 'e': 'road_2_1_2', 's': 'road_1_0_1', 'n': 'road_1_2_3'}
sumoAgent = SumoAgent(sumofile, port, inEdges, outEdges, inLanes, outLanes, I, sumoBinary='sumo')
K = 0.5
R = 0.3  # 超过
# 创建一个replayBuffer对象
capacity, minibatch = 30000, 800
replayBuffer = ReplayBuffer(capacity, minibatch)
# memory = Memory(capacity,minibatch)

# 创建一个车辆生成器
# totalNumber, maxSteps, leftTurn, straight, scale = 4000, MAX_STEPS, 4, 4,  1
# gencar = GenCar(totalNumber, maxSteps, leftTurn, straight, fileName, scale)
# gencar.gen_dynamic_demand()
# gencar.generate_routefile()

# 初始化一个agent  4+4+4+8
in_dim, mid_dim, out_dim = 20, 3 * 9, 8
learning_rate, gamma, epsilon, alpha = 0.0001, 0.95, 1, 0.3  # decay大概19轮左右
# agent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent)

C = 3
net_update_times = 0
# dqn 数据记录
total_step_list, total_per_reward_list, total_per_queue_list, total_per_delay_list, total_per_travel_list = [], [], [], [], []
total_throughput = []

# 创建一个车辆生成器
totalNumber, maxSteps, leftTurn, straight, scale = 2000, MAX_STEPS, 2, 6, 1
# 生成50个数据集，以及对应的cfg文件
for i in range(SAMPLE_SIZES):
    path = "./sumoNet3/"
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
l = [i for i in range(0, SAMPLE_SIZES)]
for epoch in range(MAX_EPOCHS):
    N = 301
    dqnagent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent, K, R)
    # print("===============================  epoch {0}  ===============================".format(epoch))
    # 随机选择30个路由文件
    choose = np.random.choice(l, MAX_EPISODES)
    queue_list, delay_list, travel_list, reward_list = [], [], [], []
    steps_list, per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []
    throughput = []
    print("=========epoch {0} start time {1} ================".format(epoch, time.time()))
    for episode in range(MAX_EPISODES):
        sumofile = './sumoNet3/net{0}.sumocfg'.format(choose[episode])
        start_time = time.time()
        mode = 'train'
        queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps,t = dqn_control_norm2(
            sumoAgent,
            sumofile, port,
            inEdges, outEdges,
            inLanes, outLanes,
            totalNumber, I,
            dqnagent,
            MAX_EPISODES,
            MAX_STEPS, in_dim,
            net_update_times,
            C,
            replayBuffer, mode)
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
        throughput.append(t)
        tt = end_time - start_time
        print("episode={0} reward={1} steps={2} speed={3} elapsed={4}".format(episode, per_reward, steps,
                                                                              round(tt / 60, 2), tt))

        # 每轮都记录一次数据 避免某次出现错误丧失数据！

        fname = 'data_save3/detail_data/data_{0}.xlsx'.format(N)
        # dqnagent.save_model(path)
        data_list = {'rewards': reward_list,
                     'delay_time': delay_list,
                     'queue': queue_list,
                     'travel_time': travel_list,
                     'per_reward': per_reward_list,
                     'per_delay_time': per_delay_list,
                     'per_queue': per_queue_list,
                     'per_travel_time': per_travel_list,
                     'throughput': throughput}
        record_data(fname, data_list)
    os.mkdir('data_save3/detail_data/data_{0}_{1}'.format(N, epoch))
    writer = SummaryWriter('data_save3/detail_data/data_{0}_{1}'.format(N,epoch))
    for i in range(len(per_reward_list)):
        writer.add_scalar('reward', per_reward_list[i], global_step=i)
        writer.add_scalar('delay_time', per_delay_list[i], global_step=i)
        writer.add_scalar('queue', per_queue_list[i], global_step=i)
        writer.add_scalar('travel time', per_travel_list[i], global_step=i)
        writer.add_scalar('throughput', throughput[i], global_step=i)
    total_per_reward_list.append(per_reward_list)
    total_per_queue_list.append(per_queue_list)
    total_per_delay_list.append(per_delay_list)
    total_per_travel_list.append(per_travel_list)
    total_step_list.append(steps_list)
    total_throughput.append(throughput)


N = 301
# 绘图
IndSummaryPlot_S(N, total_per_reward_list, 'per_reward')
IndSummaryPlot_S(N, total_per_queue_list, 'per_queue')
IndSummaryPlot_S(N, total_per_delay_list, 'per_delay')
IndSummaryPlot_S(N, total_per_travel_list, 'per_travel')
IndSummaryPlot_S(N, total_throughput, 'throughput')
IndSummaryPlot_S(N, total_step_list, 'step')
# 将数据存入excel
fname = 'data_save3/data_{0}.xlsx'.format(N)
data_list = {'step': total_step_list,
             'rewards': total_per_reward_list,
             'delay_time': total_per_delay_list,
             'queue': total_per_queue_list,
             'travel_time': total_per_travel_list,
             'throughput': total_throughput
             }
record_data_2(fname, data_list)
# 然后使用该模型进行测试 test
# 随机选取10个数据集
test_size = 50
choose = random.sample(l, test_size)
# dqn 数据记录
queue_list, delay_list, travel_list, reward_list = [], [], [], []
steps_list, per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []
throughputs = []
# ft 数据记录
ft_queue_list, ft_delay_list, ft_travel_list = [], [], []
ft_steps, ft_per_queue_list, ft_per_travel_list, ft_per_delay_list = [], [], [], []
ft_throughputs = []
# mp 数据记录
mp_queue_list, mp_delay_list, mp_travel_list = [], [], []
mp_steps, mp_per_queue_list, mp_per_delay_list, mp_per_travel_list = [], [], [], []
mp_throughputs = []
for c in range(len(choose)):
    sumofile = './sumoNet2/net{0}.sumocfg'.format(choose[c])
    start_time = time.time()
    print("==========test {0} start time {1} ============".format(c, time.time()))
    ft_queues, ft_delays, ft_travels, ft_per_queue, ft_per_delay, ft_per_travel_time, ft_step,ft_t = ft_control(sumoAgent,
                                                                                                           sumofile,
                                                                                                           port,
                                                                                                           inEdges,
                                                                                                           outEdges,
                                                                                                           inLanes,
                                                                                                           outLanes,
                                                                                                           totalNumber,
                                                                                                           MAX_STEPS,
                                                                                                           I)
    ft_queue_list.append(ft_queues)
    ft_delay_list.append(ft_delays)
    ft_travel_list.append(ft_travels)
    ft_per_queue_list.append(ft_per_queue)
    ft_per_delay_list.append(ft_per_delay)
    ft_per_travel_list.append(ft_per_travel_time)
    ft_steps.append(ft_step)
    ft_throughputs.append(ft_t)
    print('ft finished')
    mp_queues, mp_delays, mp_travels, mp_per_queue, mp_per_delay, mp_per_travel_time, mp_step,mp_t = max_pressure(sumoAgent,
                                                                                                             sumofile,
                                                                                                             port,
                                                                                                             inEdges,
                                                                                                             outEdges,
                                                                                                             inLanes,
                                                                                                             outLanes,
                                                                                                             totalNumber,
                                                                                                             MAX_STEPS,
                                                                                                             I)
    mp_queue_list.append(mp_queues)
    mp_delay_list.append(mp_delays)
    mp_travel_list.append(mp_travels)
    mp_per_queue_list.append(mp_per_queue)
    mp_per_delay_list.append(mp_per_delay)
    mp_per_travel_list.append(mp_per_travel_time)
    mp_steps.append(mp_step)
    mp_throughputs.append(mp_t)
    print("mp finished")
    mode = 'test'
    queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps,t = dqn_control_norm2(
        sumoAgent,
        sumofile,
        port,
        inEdges,
        outEdges,
        inLanes,
        outLanes,
        totalNumber, I,
        dqnagent,
        MAX_EPISODES,
        MAX_STEPS,
        in_dim,
        net_update_times,
        C,
        replayBuffer, mode)
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
    throughputs.append(t)

# 绘制图形
IndSummaryPlot_S2(N, 'test_per_reward', dqn=[per_reward_list])
IndSummaryPlot_S2(N, 'test_per_queue', ft=[ft_per_queue_list], mp=[mp_per_queue_list], dqn=[per_queue_list])
IndSummaryPlot_S2(N, 'test_per_delay', ft=[ft_per_delay_list], mp=[mp_per_delay_list], dqn=[per_delay_list])
IndSummaryPlot_S2(N, 'test_per_travel_time', ft=[ft_per_travel_list], mp=[mp_per_travel_list], dqn=[per_travel_list])
IndSummaryPlot_S2(N, 'test_throughput', ft=[ft_throughputs], mp=[mp_throughputs], dqn=[throughputs])

fname2 = 'data_save3/ft_data_{0}.xlsx'.format(N)
data_list2 = {'ft_delay_time': ft_delay_list,
              'ft_queue': ft_queue_list,
              'ft_travel_time': ft_travel_list,
              'ft_per_delay_time': ft_per_delay_list,
              'ft_per_queue': ft_per_queue_list,
              'ft_per_travel_time': ft_per_travel_list,
              'ft_steps': ft_steps
              }
record_data(fname2, data_list2)

fname3 = 'data_save3/mp_data_{0}.xlsx'.format(N)
data_list3 = {'mp_delay_time': mp_delay_list,
              'mp_queue': mp_queue_list,
              'mp_travel_time': mp_travel_list,
              'mp_per_delay_time': mp_per_delay_list,
              'mp_per_queue': mp_per_queue_list,
              'mp_per_travel_time': mp_per_travel_list,
              'mp_steps': mp_steps
              }
record_data(fname3, data_list3)

fname4 = 'data_save3/dqn_test_data_{0}.xlsx'.format(N)
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
