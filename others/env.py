import traci
class Environment:
    def __init__(self):
        pass

    def step(self,step,**kwargs):
        '''

        :param step: 整个环境要执行多少步
        :param kwargs: 传入各个agent的action 格式 {'tls_id':action}  # 目前只有一个
        :return: 返回next_obs,reward,done,_
        '''
        #  设置每个traffic的phase 然后同时执行多步
        for tls,action in kwargs.items():
            traci.trafficlight.setPhase(tls,action)


    def get_observation(self):
        # 通过sumo_agent