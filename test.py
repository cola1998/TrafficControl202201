def testModel(mode):
    if mode == 'test':
        test_size = 20
        choose = random.sample(l, test_size)
        # dqn 数据记录
        queue_list, delay_list, travel_list, reward_list = [], [], [], []
        steps_list, per_reward_list, per_queue_list, per_delay_list, per_travel_list = [], [], [], [], []

        # ft 数据记录
        ft_queue_list, ft_delay_list, ft_travel_list = [], [], []
        ft_steps, ft_per_queue_list, ft_per_travel_list, ft_per_delay_list = [], [], [], []

        # mp 数据记录
        mp_queue_list, mp_delay_list, mp_travel_list = [], [], []
        mp_steps, mp_per_queue_list, mp_per_delay_list, mp_per_travel_list = [], [], [], []

        for c in range(len(choose)):
            sumofile = './sumoNet1/net{0}.sumocfg'.format(choose[c])
            start_time = time.time()
            print("==========test {0} start time {1} ============".format(c, time.time()))
            ft_queues, ft_delays, ft_travels, ft_per_queue, ft_per_delay, ft_per_travel_time, ft_step = ft_control(
                sumoAgent,
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
            queues, delays, travel_times, rewards, per_queue, per_delay, per_travel, per_reward, steps = dqn_control(
                sumoAgent,
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
                      'ft_steps': ft_steps
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

