import torch


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
        action = agent.select_action(obs)
        next_obs, r, done = agent.take_action(action, MAX_STEPS)
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
