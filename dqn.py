import torch,time
import os,sys
from SumoAgent import SumoAgent
from agent import DQNAgent
from ReplayBuffer import ReplayBuffer

def dqn_control(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber,
                agent, MAX_EPISODES, MAX_STEPS, in_dim, net_update_times, C,
                replayBuffer):
    times = 0  # 记录agent执行动作次数
    # 一次仿真开始
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes)
    sumoAgent.start_sumo()
    obs = agent.get_state()
    done = False
    rewards, queues, delays = 0, 0, 0

    print("remain car ", sumoAgent.get_remain_cars())
    while not done or sumoAgent.get_current_time() < MAX_EPISODES:
        obs = torch.as_tensor(obs, dtype=torch.float32)
        obs = obs.view(1, in_dim)
        flag = 0  # 计算
        action = agent.select_action_biu(obs,0)
        next_obs, r, done = agent.take_action_biu(action, MAX_STEPS)
        # next_obs = torch.as_tensor(next_obs,dtype=torch.float32)
        # state_value = agent.cri(obs)[0][action]
        # next_state_value = agent.cri_target(next_obs).max(0)[0]
        # error = r + next_state_value - state_value

        rewards += r

        times += 1
        queues += sum(list(sumoAgent.get_queue1().values()))
        delays += sum(sumoAgent.get_delay_time1().values())

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

    # 存储这一轮的相关数据
    throughOutput = totalNumber - sumoAgent.get_remain_cars()  # 本次仿真通过的车辆数
    print("remain car ", sumoAgent.get_remain_cars())
    print("total step ", sumoAgent.get_current_time())

    # 指标计算
    per_queue = round(queues / throughOutput, 2)
    per_delay = round(delays / throughOutput, 2)
    travel_times = sumoAgent.get_total_travel_time()
    per_travel = sumoAgent.get_per_travel_time()
    per_reward = round(rewards / times, 2)
    sumoAgent.end_sumo()
    return queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward,times


# if __name__ == '__main__':
#     if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)
#
#     sumofile = './sumoNet1/net0.sumocfg'
#
#     port = 5905
#     inEdges = ['road_0_1_0', 'road_2_1_2', 'road_1_0_1', 'road_1_2_3']
#     outEdges = ['road_1_1_0', 'road_1_1_2', 'road_1_1_1', 'road_1_1_3']
#     inLanes = ['road_0_1_0_2', 'road_0_1_0_1', 'road_0_1_0_0',
#                'road_2_1_2_2', 'road_2_1_2_1', 'road_2_1_2_0',
#                'road_1_0_1_2', 'road_1_0_1_1', 'road_1_0_1_0',
#                'road_1_2_3_2', 'road_1_2_3_1', 'road_1_2_3_0']
#     outLanes = ['road_1_1_0_2', 'road_1_1_0_1', 'road_1_1_0_0',
#                 'road_1_1_2_2', 'road_1_1_2_1', 'road_1_1_2_0',
#                 'road_1_1_1_2', 'road_1_1_1_1', 'road_1_1_1_0',
#                 'road_1_1_3_2', 'road_1_1_3_1', 'road_1_1_3-0']
#     sumoAgent = SumoAgent(sumofile, port, inEdges, outEdges, inLanes, outLanes)
#
#     capacity, minibatch = 30000, 2000
#     replayBuffer = ReplayBuffer(capacity, minibatch)
#     totalNumber = 4000
#     in_dim, mid_dim, out_dim = 12, 3 * 9, 4
#     learning_rate, gamma, epsilon, alpha = 0.01, 0.95, 0.9, 0.3  # decay大概19轮左右
#     agent = DQNAgent(in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent)
#     MAX_EPISODES = 3
#     MAX_STEPS = 7200
#     C = 3
#     net_update_times = 0
#     queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps = dqn_control(sumoAgent,
#                                                                                                              sumofile,
#                                                                                                              port,
#                                                                                                              inEdges,
#                                                                                                              outEdges,
#                                                                                                              inLanes,
#                                                                                                              outLanes,
#                                                                                                              totalNumber,
#                                                                                                              agent,
#                                                                                                              MAX_EPISODES,
#                                                                                                              MAX_STEPS,
#                                                                                                              in_dim,
#                                                                                                              net_update_times,
#                                                                                                              C,
#                                                                                                              replayBuffer)
#     print("----start time:",time.time())
#     print("queues ",queues)
#     print("delays ",delays)
#     print("rewards ", rewards)
#     print("travel_times ",travel_times)
#     print("per_queue ", per_queue)
#     print("per_delay ", per_delay)
#     print("per_travel ", per_travel)
#     print("per_reward ", per_reward)