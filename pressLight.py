class PressLight:
    def __init__(self,sumoAgent):
        self.sumoAgent = sumoAgent

    def get_observation(self):
        '''
        function:获取观察状态
        observation 构成
        1） current phase -p
        2） each outgoing lane 车辆数x[m][k]
        3） each incoming lane 车辆数x[l][k]
        :return:
        '''
        p = self.sumoAgent.getPhase()//2
        xl = self.sumoAgent.get_queue1()
        xm = self.sumoAgent.get_queue_out()

    def get_pressure(self):
        w = []
        xl = list(self.sumoAgent.get_queue1())
        xm = list(self.sumoAgent.get_queue_out())
        return [xl[i]/xm[i] for i in range(len(xl))] # 返回四条edge的压力


    def cal_reward(self):


def run():
    pl = PressLight()
    state = pl.get_observation()
