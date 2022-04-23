from SumoAgent import SumoAgent
import traci
import os, sys
import pandas as pd


def ft_control(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber,
               MaxSteps):
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes)
    sumoAgent.start_sumo()
    delays, queues = 0, 0
    step = 0
    while True:
        now_phase = sumoAgent.getPhase()

        if now_phase == 0:
            sumoAgent.setPhase(1)
            now_phase = sumoAgent.getPhase()
        if now_phase == 1:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 1
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
            now_phase = sumoAgent.getPhase()
            last_phase = 1
            while now_phase != last_phase + 2:  # 矫正一下
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
                now_phase = sumoAgent.getPhase()
        elif now_phase == 3:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 3:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 5:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 5:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 7:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 9:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 11:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 13:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
        elif now_phase == 15:
            step += 1
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
    throughOutput = totalNumber - sumoAgent.get_remain_cars()


    per_queue = round(queues/throughOutput, 2)
    per_delay = round(delays/throughOutput, 2)
    per_travel_time = sumoAgent.get_per_travel_time()
    travels = sumoAgent.get_total_travel_time()
    sumoAgent.end_sumo()

    return queues, delays, travels, per_queue, per_delay, per_travel_time,step


def max_pressure(sumoAgent, sumofile, port, inEdges, outEdges, inLanes, outLanes, totalNumber,
                 MaxSteps):
    sumoAgent.__init__(sumofile, port, inEdges, outEdges, inLanes, outLanes)
    sumoAgent.start_sumo()

    delays, queues = 0, 0
    step = 0
    while True:
        now_phase = sumoAgent.getPhase()
        # 计算压力  选择动作
        inEdge_queue = sumoAgent.get_queue1()  # dict
        outEdge_queue = sumoAgent.get_queue_out()  # dict
        # d = {'gneE1': '-gneE3', 'gneE3': '-gneE1', 'gneE0': '-gneE2', 'gneE2': '-gneE0'}
        d = {'road_0_1_0':'road_1_1_0','road_2_1_2':'road_1_1_2','road_1_0_1':'road_1_1_1','road_1_2_3':'road_1_1_3'}
        pressure = []
        for key in d.keys():
            pressure.append(inEdge_queue[key] - outEdge_queue[d[key]])  # 压力：入度 - 出度
        a = pressure.index(max(pressure))
        if a == 0:
            now_phase = 9
        elif a == 1:
            now_phase = 11
        elif a == 2:
            now_phase = 13
        else:
            now_phase = 15

        if now_phase == 9:
            step += 1
            sumoAgent.setPhase(9)
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 1
            sumoAgent.setPhase(10)
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
            last_phase = 10
            now_phase = sumoAgent.getPhase()
            while now_phase != last_phase + 1:
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
                now_phase = sumoAgent.getPhase()
        elif now_phase == 11:
            step += 1
            sumoAgent.setPhase(11)
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 3:
            sumoAgent.setPhase(12)
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
            last_phase = 12
            now_phase = sumoAgent.getPhase()
            while now_phase != last_phase + 1:
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
                now_phase = sumoAgent.getPhase()
        elif now_phase == 13:
            step += 1
            sumoAgent.setPhase(13)
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 5:
            sumoAgent.setPhase(14)
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break
            last_phase = 14
            now_phase = sumoAgent.getPhase()
            while now_phase != last_phase + 1:
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
                now_phase = sumoAgent.getPhase()
        elif now_phase == 15:
            step += 1
            sumoAgent.setPhase(15)
            for i in range(30):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            # phase = 7:
            sumoAgent.setPhase(16)
            for i in range(3):
                sumoAgent.sim_step()
                sumoAgent.update_travel_times()
            queues += sum(list(sumoAgent.get_queue1().values()))
            delays += sum(list(sumoAgent.get_delay_time1().values()))
            if sumoAgent.get_current_time() >= MaxSteps:
                break

    throughOutput = totalNumber - sumoAgent.get_remain_cars()
    per_queue = round(queues/throughOutput, 2)
    per_delay = round(delays/throughOutput, 2)
    per_travel_time = sumoAgent.get_per_travel_time()
    travels = sumoAgent.get_total_travel_time()
    sumoAgent.end_sumo()

    return queues, delays, travels,per_queue, per_delay, per_travel_time,step


# if __name__ == '__main__':
#     if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)
#
#     sumofile = '../sumoNet1/net0.sumocfg'
#
#     port = 5905
#
#     # inEdges = ['gneE1', 'gneE3', 'gneE0', 'gneE2']
#     # outEdges = ['-gneE1', '-gneE3', '-gneE0', '-gneE2']
#     # inLanes = ['gneE1_0', 'gneE1_1', 'gneE1_2',
#     #            'gneE3_0', 'gneE3_1', 'gneE3_2',
#     #            'gneE0_0', 'gneE0_1', 'gneE0_2',
#     #            'gneE2_0', 'gneE2_1', 'gneE2_2'
#     #            ]
#     # outLanes = ['-gneE1_0', '-gneE1_1', '-gneE1_2',
#     #             '-gneE3_0', '-gneE3_1', '-gneE3_2',
#     #             '-gneE0_0', '-gneE0_1', '-gneE0_2',
#     #             '-gneE2_0', '-gneE2_1', '-gneE2_2'
#     #             ]
#
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
#     sumoAgent = SumoAgent(sumofile, port, inEdges, outEdges, inLanes, outLanes, sumoBinary='sumo')
#     ft_queues, ft_delays, ft_travels, ft_per_queue, ft_per_delay, ft_per_travel_time, ft_step = ft_control(sumoAgent,
#                                                                                                            sumofile,
#                                                                                                            port,
#                                                                                                            inEdges,
#                                                                                                            outEdges,
#                                                                                                            inLanes,
#                                                                                                            outLanes,
#                                                                                                            4000,
#                                                                                                            7200)
#     print("queue ", ft_queues)
#     print("delay ", ft_delays)
#     print('travel time',ft_travels)
#     print('per queue',ft_per_queue)
#     print("per delay",ft_per_delay)
#     print('per travel time', ft_per_travel_time)

#
# if __name__ == '__main__':
#     if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)
#
#     sumofile = '../sumoNet1/net0.sumocfg'
#
#     port = 5905
#
#     # inEdges = ['gneE1', 'gneE3', 'gneE0', 'gneE2']
#     # outEdges = ['-gneE1', '-gneE3', '-gneE0', '-gneE2']
#     # inLanes = ['gneE1_0', 'gneE1_1', 'gneE1_2',
#     #            'gneE3_0', 'gneE3_1', 'gneE3_2',
#     #            'gneE0_0', 'gneE0_1', 'gneE0_2',
#     #            'gneE2_0', 'gneE2_1', 'gneE2_2'
#     #            ]
#     # outLanes = ['-gneE1_0', '-gneE1_1', '-gneE1_2',
#     #             '-gneE3_0', '-gneE3_1', '-gneE3_2',
#     #             '-gneE0_0', '-gneE0_1', '-gneE0_2',
#     #             '-gneE2_0', '-gneE2_1', '-gneE2_2'
#     #             ]
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
#     totalNumber = 4000
#     mp_queues, mp_delays, mp_travels, mp_per_queue, mp_per_delay, mp_per_travel_time, mp_step = max_pressure(sumoAgent,
#                                                                                                              sumofile,
#                                                                                                              port,
#                                                                                                              inEdges,
#                                                                                                              outEdges,
#                                                                                                              inLanes,
#                                                                                                              outLanes,
#                                                                                                              totalNumber,
#                                                                                                              7200)
#     print("queue ", mp_queues)
#     print("delay ", mp_delays)
#     print("travel time",mp_travels)
#     print("per queue", mp_per_queue)
#     print("per delay", mp_per_delay)
#     print("per travel", mp_per_travel_time)
#
