import torch, time
import os, sys
from SumoAgent import SumoAgent
from agent import DQNAgent
from ReplayBuffer import ReplayBuffer


def dqn_control(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber, I,
                agent, MAX_EPISODES, MAX_STEPS, in_dim, net_update_times, C,
                replayBuffer, mode):
    times = 0  # 记录agent执行动作次数
    # 一次仿真开始
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes, I)
    sumoAgent.start_sumo()
    obs = agent.get_state()
    done = False
    rewards, queues, delays = 0, 0, 0
    per_delays = 0

    print("remain car ", sumoAgent.get_remain_cars())
    if mode != 'test':

        while not done or sumoAgent.get_current_time() < MAX_EPISODES:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            obs = obs.view(1, in_dim)

            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs
            agent.optimize_model()
            net_update_times += 1

            if net_update_times % C == 0:
                agent.optimize_target_model()
    else:
        # mode = 'test'   不更新网络了
        while not done or sumoAgent.get_current_time() < MAX_EPISODES:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            obs = obs.view(1, in_dim)

            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs

    # 存储这一轮的相关数据
    throughOutput = totalNumber - sumoAgent.get_remain_cars()  # 本次仿真通过的车辆数
    print("remain car ", sumoAgent.get_remain_cars())
    print("total step ", sumoAgent.get_current_time())

    # 指标计算
    per_queue = round(queues / throughOutput, 2)
    per_delay = round(per_delays / (4 * times), 2)
    travel_times = sumoAgent.get_total_travel_time()
    per_travel = sumoAgent.get_per_travel_time()
    per_reward = round(rewards / times, 2)
    sumoAgent.end_sumo()
    return queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, times


def dqn_control_norm(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber, I,
                agent, MAX_EPISODES, MAX_STEPS, in_dim, net_update_times, C,
                replayBuffer, mode):
    times = 0  # 记录agent执行动作次数
    # 一次仿真开始
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes, I)
    sumoAgent.start_sumo()
    obs = agent.get_norm_state()
    done = False
    rewards, queues, delays = 0, 0, 0
    per_delays = 0

    # print("remain car ", sumoAgent.get_remain_cars())
    if mode != 'test':

        while not done or sumoAgent.get_current_time() < MAX_EPISODES:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            # print("in_dim ", in_dim)
            obs = obs.view(1, in_dim)
            # print("obs ", obs)
            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu_norm(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs
            agent.optimize_model()
            net_update_times += 1

            if net_update_times % C == 0:
                agent.optimize_target_model()
    else:
        # mode = 'test'   不更新网络了
        while not done or sumoAgent.get_current_time() < MAX_EPISODES:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            obs = obs.view(1, in_dim)

            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu_norm(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs

    # 存储这一轮的相关数据
    throughOutput = totalNumber - sumoAgent.get_remain_cars()  # 本次仿真通过的车辆数
    print("dqn throughput", throughOutput)
    # print("dqn remain car",sumoAgent.get_remain_cars())
    # print("len travel_times ",len(sumoAgent.v_travel_times))
    # print("total step ", sumoAgent.get_current_time())

    # 指标计算
    per_queue = round(queues / throughOutput, 2)
    per_delay = round(per_delays / (4 * times), 2)
    travel_times = sumoAgent.get_total_travel_time()
    per_travel = sumoAgent.get_per_travel_time()
    per_reward = round(rewards / times, 2)
    sumoAgent.end_sumo()
    return queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, times, throughOutput

def dqn_control_norm2(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber, I,
                agent, MAX_EPISODES, MAX_STEPS, in_dim, net_update_times, C,
                replayBuffer, mode):
    times = 0  # 记录agent执行动作次数
    # 一次仿真开始
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes, I)
    sumoAgent.start_sumo()
    obs = agent.get_norm_state()
    done = False
    rewards, queues, delays = 0, 0, 0
    per_delays = 0

    # print("remain car ", sumoAgent.get_remain_cars())
    if mode != 'test':

        while sumoAgent.get_remain_cars() > 0:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            # print("in_dim ", in_dim)
            obs = obs.view(1, in_dim)
            # print("obs ", obs)
            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu_norm_2(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs
            agent.optimize_model()
            net_update_times += 1

            if net_update_times % C == 0:
                agent.optimize_target_model()
    else:
        # mode = 'test'   不更新网络了
        while sumoAgent.get_remain_cars() > 0:
            obs = torch.as_tensor(obs, dtype=torch.float32)
            obs = obs.view(1, in_dim)

            action = agent.select_action_biu(obs)
            next_obs, r, done = agent.take_action_biu_norm_2(action, MAX_STEPS)
            # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
            # state_value = agent.cri(obs)[0][action]
            # next_state_value = agent.cri_target(next_obs).max(0)[0]
            # error = r + next_state_value - state_value

            rewards += r

            times += 1
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(sumoAgent.get_delay_time1().values())
            per_delays += sum(sumoAgent.get_per_delay_time1())

            if obs[:8] == [0, 0, 0, 0, 0, 0, 0, 0]:
                pass
            else:
                replayBuffer.append_buffer(obs, action, next_obs, r, done)
                # td-error q现实-q估计
                # memory.add(error, obs, action, next_obs, r, done)

            obs = next_obs

    # 存储这一轮的相关数据
    throughOutput = totalNumber - sumoAgent.get_remain_cars()  # 本次仿真通过的车辆数
    print("dqn throughput", throughOutput)
    # print("dqn remain car",sumoAgent.get_remain_cars())
    # print("len travel_times ",len(sumoAgent.v_travel_times))
    # print("total step ", sumoAgent.get_current_time())

    # 指标计算
    per_queue = round(queues / throughOutput, 2)
    per_delay = round(per_delays / (4 * times), 2)
    travel_times = sumoAgent.get_total_travel_time()
    per_travel = sumoAgent.get_per_travel_time()
    per_reward = round(rewards / times, 2)
    sumoAgent.end_sumo()
    return queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, times, throughOutput

if __name__ == '__main__':
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)

    sumofile = './sumoNet/reality_network/cityflow_data/hangzhou_1x1_bc-tyc_18041607_1h/net.sumocfg'

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

    capacity, minibatch = 30000, 2000
    replayBuffer = ReplayBuffer(capacity, minibatch)
    totalNumber = 2000
    in_dim, mid_dim, out_dim = 20, 3 * 9, 8
    learning_rate, gamma, epsilon, alpha = 0.01, 0.95, 0.9, 0.3  # decay大概19轮左右
    K = 0.5
    R = 0.3  # 超过
    agent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent,K,R)
    MAX_EPISODES = 3
    MAX_STEPS = 3600
    C = 3
    net_update_times = 0
    queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps,t = dqn_control_norm2(sumoAgent,
                                                                                                             sumofile,
                                                                                                             port,
                                                                                                             inEdges,
                                                                                                             outEdges,
                                                                                                             inLanes,
                                                                                                             outLanes,
                                                                                                             totalNumber,I,
                                                                                                             agent,
                                                                                                             MAX_EPISODES,
                                                                                                             MAX_STEPS,
                                                                                                             in_dim,
                                                                                                             net_update_times,
                                                                                                             C,
                                                                                                             replayBuffer,'test')
    print("----start time:",time.time())
    print("queues ",queues)
    print("delays ",delays)
    print("rewards ", rewards)
    print("travel_times ",travel_times)
    print("per_queue ", per_queue)
    print("per_delay ", per_delay)
    print("per_travel ", per_travel)
    print("per_reward ", per_reward)
    print('throughput ',t)
