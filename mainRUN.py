import torch
import os
import sys
from ReplayBuffer import ReplayBuffer
from memeory import Memory
from SumoAgent import SumoAgent
from genCar import GenCar
from agent import DQNAgent
from plots import mplot, record_data, IndSummaryPlot
from fixedTime.ft_controller import ft_control,max_pressure
from dqn import dqn_control

MAX_EPISODES = 50
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
totalNumber, maxSteps, leftTurn, straight, fileName, scale = 4000, MAX_STEPS, 4, 4, "./sumoNet/test3.rou.xml", 1
gencar = GenCar(totalNumber, maxSteps, leftTurn, straight, fileName, scale)
# gencar.gen_dynamic_demand()
# gencar.generate_routefile()

# 初始化一个agent
in_dim, mid_dim, out_dim = 12, 3 * 9, 4
learning_rate, gamma, epsilon, alpha = 0.001, 0.95, 0.9, 0.3  # decay大概19轮左右
agent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent)

C = 5
net_update_times = 0
# dqn 数据记录
queue_list, delay_list, travel_list, reward_list = [], [], [], []
steps_list,per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []

# ft 数据记录
ft_queue_list, ft_delay_list, ft_travel_list = [], [], []
ft_steps,ft_per_queue_list, ft_per_travel_list, ft_per_delay_list = [], [], [], []

# mp 数据记录
mp_queue_list, mp_delay_list, mp_travel_list = [], [], []
mp_steps, mp_per_queue_list, mp_per_delay_list, mp_per_travel_list = [], [], [], []

for episode in range(MAX_EPISODES):
    # 动态生成车辆
    gencar.gen_dynamic_demand()
    gencar.generate_routefile()

    print("episode ", episode)

    ft_queues, ft_delays, ft_travels, ft_per_queue, ft_per_delay, ft_per_travel_time,ft_step = ft_control(sumoAgent,
                                                                                                  sumofile,
                                                                                                  port, inEdges,
                                                                                                  outEdges, inLanes,
                                                                                                  outLanes, totalNumber,MAX_STEPS)
    ft_queue_list.append(ft_queues)
    ft_delay_list.append(ft_delays)
    ft_travel_list.append(ft_travels)
    ft_per_queue_list.append(ft_per_queue)
    ft_per_delay_list.append(ft_per_delay)
    ft_per_travel_list.append(ft_per_travel_time)
    ft_steps.append(ft_step)
    print('ft finished')
    mp_sumofile = './sumoNet/net2.sumocfg'
    mp_queues, mp_delays, mp_travels, mp_per_queue, mp_per_delay, mp_per_travel_time,mp_step = max_pressure(sumoAgent, mp_sumofile, port, inEdges,
                                                                                  outEdges, inLanes, outLanes,
                                                                                  totalNumber,
                                                                                  MAX_STEPS)
    mp_queue_list.append(mp_queues)
    mp_delay_list.append(mp_delays)
    mp_travel_list.append(mp_travels)
    mp_per_queue_list.append(mp_per_queue)
    mp_per_delay_list.append(mp_per_delay)
    mp_per_travel_list.append(mp_per_travel_time)
    mp_steps.append(mp_step)
    print("mp finished")

    queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward,steps = dqn_control(sumoAgent,
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

    queue_list.append(queues)
    delay_list.append(delays)
    travel_list.append(travel_times)
    reward_list.append(rewards)
    per_reward_list.append(per_reward)
    per_queue_list.append(per_queue)
    per_delay_list.append(per_delay)
    per_travel_list.append(per_travel)
    steps_list.append(steps)
    print('dqn finished')
    # 每轮都记录一次数据 避免某次出现错误丧失数据！
    N = 6
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

N = 6

# 绘图
mplot(per_reward_list, 'per_reward', N)
# mplot(per_queue_list, 'queues', N)
# mplot(per_delay_list, 'delays', N)
# mplot(ft_per_queue_list, 'ft_queues', N)
# mplot(ft_per_delay_list, 'ft_delays', N)
# mplot(ft_travel_list, 'ft_travel_time', N)

IndSummaryPlot(N, 'queue', 'delay', 'travel', ft=[ft_per_queue_list, ft_per_delay_list, ft_per_travel_list],
               dqn=[per_queue_list, per_delay_list, per_travel_list],
               mp=[mp_per_queue_list, mp_per_delay_list, mp_per_travel_list])
# 将数据存入excel
fname = 'data_save/data_{0}.xlsx'.format(N)
data_list = {'rewards': reward_list,
             'delay_time': delay_list,
             'queue': queue_list,
             'travel_time': travel_list,
             'per_reward': per_reward_list,
             'per_delay_time': per_delay_list,
             'per_queue': per_queue_list,
             'per_travel_time': per_travel_list,
             "steps": steps_list
             }
record_data(fname, data_list)

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
