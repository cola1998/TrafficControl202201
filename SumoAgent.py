import traci
import datetime


class SumoAgent:
    def __init__(self, sumofile, port, inEdges, outEdges, inLanes, outLanes, sumoBinary='sumo'):
        self.sumoBinary = sumoBinary  # 'sumo-gui'
        self.sumofile = sumofile  # '../DQN/unbalance_net/net.sumocfg'
        self.sumoConfig = [self.sumoBinary, '-c', self.sumofile, "--tripinfo-output", "tripinfo.xml"]  # 需要查阅是否需要设置port
        self.tlsID = 'gneJ0'

        # traci.edge.getIDList()
        self.inEdges = inEdges
        self.outEdges = outEdges
        self.inLanes = inLanes
        self.outLanes = outLanes

        self.time_since_last_phase_change = 0
        self.yellow_time = 3
        self.is_yellow = False
        self.nowPhase = 0
        self.nextPhase = 1
        self.free_speed = 0

        self.t = 0  # 记录now_time
        self.v_start_time = {}
        self.v_travel_times = {}
        self.last_queue = 0
        self.last_delay_time = 0
        # 待定参数
        # 1.奖励权重
        self.c1 = 1
        self.c2 = 1
        self.c3 = 0
        # 2.绿灯时间
        self.green_time = 30
        self.last_action_time = 0
        self.min_t = 10
        self.max_t = 50

    # ----- connect -----
    def start_sumo(self):
        traci.start(self.sumoConfig)
        print('----start time: ', datetime.datetime.now())
        self.tlsID = traci.trafficlight.getIDList()[0]
        self.setPhase(self.nowPhase)  # 信号灯相位从0开始
        self.sim_step()  # 先执行一步
        self.free_speed = traci.lane.getMaxSpeed(self.inLanes[0])

    def end_sumo(self):
        traci.close()
        # print("sumo close")

    def get_remain_cars(self):
        return traci.simulation.getMinExpectedNumber()

    # -----  Traffic Signal -----
    def setPhase(self, p):
        traci.trafficlight.setPhase(self.tlsID, p)

    def getPhase(self):
        return traci.trafficlight.getPhase(self.tlsID)

    def update(self):
        self.time_since_last_phase_change += 1
        if self.is_yellow and self.time_since_last_phase_change == self.yellow_time:
            traci.trafficlight.setPhase(self.tlsID, self.nextPhase)
            self.is_yellow = False

    # ----- environment -----
    def sim_step(self):
        traci.simulationStep()
        self.t += 1

    def step(self, current_action, n_step):
        self.nowPhase = self.getPhase() # 校正一下 如果不对的话
        last_phase = self.nowPhase
        # print("last_phase ", last_phase)
        self.nowPhase = current_action * 2
        # print("nowPhase ", self.nowPhase)
        # 可选action的list [0,1,2,3]
        # print(list(self.get_queue1().values()))
        self.last_queue = sum(list(self.get_queue1().values()))
        self.last_delay_time = sum(list(self.get_per_delay_time1()))
        if last_phase != self.nowPhase:  # 需要切换
            self.setPhase((last_phase + 1) % 8)
            for i in range(3):
                self.sim_step()
                self.update_travel_times()

            self.setPhase(self.nowPhase)
            for i in range(n_step):
                self.sim_step()
                self.update_travel_times()
        else:  # 不需要切换
            for i in range(n_step):
                self.sim_step()
                self.update_travel_times()
        self.state = self.get_observation()
        r = self.compute_reward()
        return self.state, r

    def update_travel_times(self):
        for v in traci.simulation.getDepartedIDList():
            self.v_start_time[v] = self.t

        for v in traci.simulation.getArrivedIDList():  # 等到车走完才计算travel_time
            if v not in self.v_start_time:
                self.v_start_time[v] = self.t
            self.v_travel_times[v] = self.t - self.v_start_time[v]
            del self.v_start_time[v]

    def get_current_time(self):
        return self.t

    def get_observation(self):
        # phase 采用独热编码？？
        p = [0 for i in range(4)]
        p[self.getPhase() // 2] = 1
        # p = [self.getPhase()//2]

        # queue
        q = self.get_queue1()  # 4维
        # print(q)

        queue =list(q.values())

        # delay time
        delay = list(self.get_per_delay_time1())
        turning_number = list(self.get_turn_number().values())

        self.state = queue+turning_number+p
        # print("state1: ", self.state)
        # print("state2: ", list(self.get_queue2().values())+list(self.get_per_delay_time2().values()))
        return self.state

    def get_queue1(self):
        queue = {edge: 0 for edge in self.inEdges}
        n = {edge: 0 for edge in self.inEdges}
        veh_list = self.get_running_cars()

        for veh in veh_list:
            edge = traci.vehicle.getRoadID(veh)
            # print("edge ",edge)
            if edge[0] != '-' and edge[0] != ':':
                x = int(edge[4])
                if x >= 4:  # 如果是后面的edge 那么减去4 否则不变
                    edge = edge[:4] + str(x - 4) + edge[5:]
                if traci.vehicle.getSpeed(veh) < 0.1:
                   queue[edge] += 1
        return queue

    def get_queue_out(self):
        queue = {edge: 0 for edge in self.outEdges}
        n = {edge: 0 for edge in self.outEdges}
        veh_list = self.get_running_cars()

        for veh in veh_list:
            edge = traci.vehicle.getRoadID(veh)
            # print("edge ",edge)
            if edge[0] == '-' and edge[0] != ':':
                x = int(edge[5])
                if x >= 4:  # 如果是后面的edge 那么减去4 否则不变
                    edge = edge[:5] + str(x - 4) + edge[6:]
                if traci.vehicle.getSpeed(veh) < 0.1:
                   queue[edge] += 1
        return queue

    def get_queue2(self):
        queue = {}
        for edge in self.inEdges:
            cnt = 0
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                if traci.vehicle.getSpeed(vehicle) < 0.1:
                    cnt += 1
            x = str(int(edge[4])+4)
            lane2 = edge[:4]+x+edge[5:]
            for vehicle in traci.edge.getLastStepVehicleIDs(lane2):
                if traci.vehicle.getSpeed(vehicle) < 0.1:
                    cnt += 1
            queue[edge] = cnt
        return queue

    def get_queue_n(self):
        n = 0
        for edge in self.inEdges:
            n += traci.edge.getLastStepVehicleIDs(edge)

            x = str(int(edge[4]) + 4)
            edge2 = edge[:4] + x + edge[5:]
            n += traci.edge.getLastStepVehicleIDs(edge)
        return n

    def get_total_travel_time(self):
        res = 0
        for k, v in self.v_travel_times.items():
            res += v
        return res

    def get_travel_time(self):
        return self.v_travel_times

    def get_running_cars(self):
        return list(self.v_start_time.keys())

    def get_per_travel_time(self):
        res = 0
        num = 0
        for k, v in self.v_travel_times.items():
            res += v
            num += 1
        if num == 0:
            return 0
        return round(res / num, 2)

    def get_per_delay_speed(self): # 暂时不用
        delay = 0
        num = 0
        for edge in self.inEdges:
            free_speed = traci.lane.getMaxSpeed(edge)
            num += len(traci.lane.getLastStepVehicleIDs(edge))
            for veh in traci.lane.getLastStepVehicleIDs(edge):
                speed = traci.vehicle.getSpeed(veh)
                d = 1 - speed / free_speed
                delay += d
        if num == 0:
            return 0
        return round(delay / num, 2)

    def get_v_delay_time(self, free_speed, veh):
        self.update_travel_times()
        dis = traci.vehicle.getDistance(veh)
        free_t = round(dis / free_speed, 5)
        if veh in self.v_travel_times:
            d = free_t - self.v_travel_times[veh]
        else:
            self.v_travel_times[veh] = 0
            d = free_t - self.v_travel_times[veh]
        return d

    def get_delay_time1(self):
        # 延迟时间 = 自由行驶时间 - 实际行驶时间
        delay = {edge:0 for edge in self.inEdges}
        veh_list = self.get_running_cars()
        free_speed = self.free_speed
        for veh in veh_list:
            edge = traci.vehicle.getRoadID(veh)
            if edge[0] != '-' and edge[0] != ':':
                x = int(edge[4])
                if x >= 4:  # 如果是后面的edge 那么减去4 否则不变
                    edge = edge[:4] + str(x-4) + edge[5:]
                delay[edge] += self.get_v_delay_time(free_speed, veh)
        return delay


    def get_per_delay_time1(self):
        # 延迟时间 = 自由行驶时间 - 实际行驶时间 4维
        delay = {edge: 0 for edge in self.inEdges}
        n = {edge:0 for edge in self.inEdges}
        veh_list = self.get_running_cars()
        free_speed = self.free_speed
        for veh in veh_list:
            edge = traci.vehicle.getRoadID(veh)
            if edge[0] != '-' and edge[0] != ':':
                x = int(edge[4])
                if x >= 4:  # 如果是后面的edge 那么减去4 否则不变
                    edge = edge[:4] + str(x - 4) + edge[5:]
                delay[edge] += self.get_v_delay_time(free_speed, veh)
                n[edge] += 1
        per_delay = []
        for i in delay.keys():
            if n[i] != 0:
                per_delay.append(round(delay[i] / n[i], 4))
            else:
                per_delay.append(0)
        return per_delay


    def get_per_waiting_time(self):
        total_waiting_time = 0
        num = 0
        for lane in self.inLanes:
            veh_list = traci.lane.getLastStepVehicleIDs(lane)
            waiting_time = 0
            num += len(veh_list)
            for veh in veh_list:
                waiting_time += traci.vehicle.getAccumulatedWaitingTime(veh)
            total_waiting_time += waiting_time
        if num == 0:
            return 0
        return round(total_waiting_time / num, 2)

    def compute_reward(self):
        per_delay_time = sum(self.get_per_delay_time1())

        queue = sum(list(self.get_queue1().values()))
        per_travel_time = self.get_per_travel_time()
        # reward = -self.c1 * per_delay_time - self.c2 * queue - self.c3*per_travel_time
        # print("reward: ", reward)

        # reward = self.last_queue - queue + self.last_delay_time - per_delay_time
        reward = per_delay_time + per_travel_time
        return -1*reward

    def normalization(self, x):
        nor_x = {}
        min_x = min(x)
        for lane in self.inLanes:
            nor_x[lane] = round(x[lane] / min_x, 5)
        return nor_x

    def pressMetric(self,k):
        '''
        state组成：p 当前阶段 动作WES,WEL,NSS,NSL 跟我们的相位方案一致
        :param k: k = 3 车道分的段数
        :return:
        xm[k=0,1,2]出车道车辆数  xl[k= 0,1,2]入车道车辆数 x_max是车道上允许的最大车辆数
        w(l,m) = xl/xl_max - xm/xm_max
        pressure = w(l,m)[k=0,1,2] 之和 reward=-pressure
        '''
        pass

    def get_turn_number(self):
        turn_list = {edge: 0 for edge in self.inEdges}
        n = {edge:0 for edge in self.inEdges}
        veh_list = self.get_running_cars()

        for veh in veh_list:
            edge = traci.vehicle.getRoadID(veh)
            # route = list(traci.vehicle.getRoute(veh))
            # next_edge = route[route.index(now_edge) + 1]
            if edge[0] != '-' and edge[0] != ':':
                x = int(edge[4])
                if x >= 4:  # 如果是后面的edge 那么减去4 否则不变
                    edge = edge[:4] + str(x - 4) + edge[5:]
                # 左转
                if veh[:3] == 'N_E' or veh[:3] == 'S_W' or veh[:3] == 'E_N' or veh[:3] == 'W_S':
                    turn_list[edge] += 1

        return turn_list