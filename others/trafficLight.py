import traci


class TrafficLight:
    def __init__(self, inLanes, outLane, inEdge, outEdge, environment):
        # 巴拉巴拉
        self.id = tsl_id
        self.env = environment  # 当前所处环境

        self.min_green = min_green
        self.max_green = max_green
        self.green_phase = 0  # 绿灯相位
        self.duration = 0  # 记录当前相位持续时间
        self.phase = 0  # 记录当前相位
        self.t = 0  # 记录当前时间
        self.is_yellow = False

        self.inLanes = []
        self.outLanes = []
        self.inEdges = []
        self.outEdges = []

        self.observation_space = []
        self.action_space = [i for i in range(action_dim)]

    def getPhase(self):
        self.phase = traci.trafficlight.getPhase(self.id)
        return self.phase

    def update(self):
        pass

    def getState(self):



    def sim_step(self):
        '''
        sumo执行 更新t
        :return:
        '''
        traci.simulationStep()  # 执行一步
        self.t += 1

    def changeAction(self, new_action):
        while new_action == self.phase:
            new_action = self.agent.select_action(self.state)
        return new_action

    def step(self, new_action, nsteps):
        '''

        :param new_action: 设置的相位
        :param step:  n需要执行的步数
        :return:
        '''
        self.phase = new_action
        traci.trafficlight.setPhase(self.id, self.phase)
        for _ in nsteps:
            self.sim_step()

    def takeAction(self, new_action):
        if self.phase == new_action:
            #  不需要切换

            #  判断是否超过最大时间了
            if self.duration + self.green_phase > self.max_green:
                # 重新随机选一个
                new_action = self.changeAction(new_action)

                # 先执行一个过渡黄灯
                nsteps = 3
                self.step(self.phase + 1, nsteps)

                nsteps = 30
                self.step(new_action*2, nsteps)
                self.duration = nsteps

            else:
                # 直接执行
                nsteps = 30
                self.step(new_action*2, nsteps)
                self.duration += nsteps
        else:
            # 需要切换
            nsteps = 3
            self.step(self.phase + 1, nsteps)

            nsteps = 30
            self.step(new_action*2, nsteps)
            self.duration = nsteps
