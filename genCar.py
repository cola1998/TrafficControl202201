import numpy as np
import math


class GenCar:
    def __init__(self, totalNumber, maxSteps, leftTurn, straight, fileName,scale):
        self.totalNumber = totalNumber  # 代表车辆总数
        self.maxSteps = maxSteps  # 代表车辆可出现的时间段

        self.idealLeft = leftTurn
        self.idealStraight = straight

        self.realLeft = 0
        self.realStraight = 0
        self.realRight = 1 - self.realLeft - self.realStraight
        self.fileName = fileName  # 代表要写入的路径文件名
        # self.sumoAgent = sumoAgent
        self.origins = ['gneE4','gneE5','gneE6','gneE7']
        self.aims = ['-gneE4', '-gneE5', '-gneE6', '-gneE7']
        self.scale = scale #0.8  # 调节生成车辆数 1500 - 0.8

    def generate_routefile(self):
        if self.idealLeft + self.idealStraight > 9:
            print("生成文件失败，请重新检查车流转向比例！两者之和为 ", self.idealLeft + self.idealStraight)
            return False
        # 汽车的生成根据weibull分布 生成N辆车
        timings = np.random.weibull(2, self.totalNumber)  # N辆车产生的时间按照weibull分布
        timings = np.sort(timings)

        # print("timings", len(timings))
        # 重新调整 以适应0：maxStep的间隔
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        # print(min_old)
        # print(max_old)
        min_new = 0
        max_new = self.maxSteps

        for value in timings:
            tmp = ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new

            car_gen_steps = np.append(car_gen_steps, tmp)
        car_gen_steps = np.rint(car_gen_steps)  # 将数组的元素四舍五入到最接近的整数
        # print(car_gen_steps)
        # 生成汽车路径文件 每行一辆车
        with open(self.fileName, 'w') as routes:
            print("""<routes>
            <vType id="standard_car" length="3.0" maxSpeed="15" minGap="1.0" accel="1.0" decel="4.0" />
            <route id="N_S" edges="road_1_2_3 road_1_1_3"/>
            <route id="N_E" edges="road_1_2_3 road_1_1_0"/>
            <route id="N_W" edges="road_1_2_3 road_1_1_2"/>
            <route id="S_W" edges="road_1_0_1 road_1_1_2"/>
            <route id="S_E" edges="road_1_0_1 road_1_1_0"/>
            <route id="S_N" edges="road_1_0_1 road_1_1_1"/>
        
            <route id="W_E" edges="road_0_1_0 road_1_1_0"/>
            <route id="W_N" edges="road_0_1_0 road_1_1_1"/>
            <route id="W_S" edges="road_0_1_0 road_1_1_3"/>
            <route id="E_N" edges="road_2_1_2 road_1_1_1"/>
            <route id="E_S" edges="road_2_1_2 road_1_1_3"/>
            <route id="E_W" edges="road_2_1_2 road_1_1_2"/>
            """, file=routes)
            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()  # 生成一个01随机数、
                if straight_or_turn < self.idealStraight * 0.1:  # 50%机会直行
                    route_straight = np.random.randint(1, 5)
                    if route_straight == 1:
                        print(
                            "    <vehicle id='W_E_%i' type='standard_car' route='W_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_straight == 2:
                        print(
                            "    <vehicle id='E_W_%i' type='standard_car' route='E_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_straight == 3:
                        print(
                            "    <vehicle id='N_S_%i' type='standard_car' route='N_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    else:
                        print(
                            "    <vehicle id='S_N_%i' type='standard_car' route='S_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                elif straight_or_turn < self.idealLeft * 0.1:  # 25%左转
                    route_turn = np.random.randint(1, 5)  # 选择一个随机的源目的地
                    if route_turn == 1:
                        print(
                            "    <vehicle id='S_W_%i' type='standard_car' route='S_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 2:
                        print(
                            "    <vehicle id='W_N_%i' type='standard_car' route='W_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 3:
                        print(
                            "    <vehicle id='N_E_%i' type='standard_car' route='N_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 4:
                        print(
                            "    <vehicle id='E_S_%i' type='standard_car' route='E_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                else:  # 25%右转
                    route_turn = np.random.randint(1, 5)  # 选择一个随机的源目的地
                    if route_turn == 1:
                        print(
                            "    <vehicle id='S_E_%i' type='standard_car' route='S_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 2:
                        print(
                            "    <vehicle id='W_S_%i' type='standard_car' route='W_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 3:
                        print(
                            "    <vehicle id='N_W_%i' type='standard_car' route='N_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
                    elif route_turn == 4:
                        print(
                            "    <vehicle id='E_N_%i' type='standard_car' route='E_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                car_counter, step), file=routes)
            print("</routes>", file=routes)
        self.update_info()

    def gen_dynamic_demand(self):  # 不能够指定总共生成车的数量
        if self.idealLeft + self.idealStraight > 9:
            print("生成文件失败，请重新检查车流转向比例！两者之和为 ", self.idealLeft + self.idealStraight)
            return False

        sim_len = self.maxSteps  # 360*2
        t = np.linspace(np.pi, 2 * np.pi, self.maxSteps)
        sine = np.sin(t) + 1.55

        v_schedule = []  # 为模拟中每秒产生的车辆数量创建时间表
        second = 1.0
        for t in range(int(self.maxSteps)):
            n_veh = 0.0
            while second > 0.0:
                headway = np.random.exponential(sine[t], size=1)
                # 获取指数分布的随机样本并返回numpy数组的样本。scale-比率的倒数（请参阅泊松分布中的lam）默认为1.0。size-返回数组的形状
                second -= headway
                if second > 0.0:
                    n_veh += 1
            second += 1.0
            v_schedule.append(int(n_veh))


        ### randomly shift traffic pattern as a form of data augmentation
        # 随机转移交通模式作为数据增强的一种形式
        v_schedule = np.array(v_schedule)
        random_shift = np.random.randint(0, sim_len)  # 随机产生一个数
        v_schedule = np.concatenate((v_schedule[random_shift:], v_schedule[:random_shift]))  # 前后交换
        ###zero out the last minute for better comparisons because of random shift
        # 由于随机转移的原因，为了更好地进行比较，在最后一分钟进行清零
        v_schedule[-60:] = 0

        ### randomly select from origins, these are where vehicles are generated
        # 从源头随机选择，这些是车辆产生的地方。
        origins = self.origins
        v_schedule = [np.random.choice(origins, size=int(self.scale * n_veh), replace=True)
                      if n_veh > 0 else [] for n_veh in v_schedule]
        # np.random.choice(a,size,replace=True,p=None) 从a中随机选择数字，构成size大小的结果返回.a必须是一维的
        # replace=True 表示可以取相同的数字 False 表示不可以取相同的数字
        # p 与数组a对应大小，表示取每个元素的概率,默认情况下取每个元素的概率相同
        ###fancy iterator, just so we can call next for sequential access
        # 花式迭代器，这样我们就可以调用下一个来进行顺序访问。
        # v_schedule = [[],array(['gne_1'], dtype='<U5'),[],[],array(['gne_3'], dtype='<U5'),[],array(['gne_5', 'gne_6'], dtype='<U5')]

        with open(self.fileName, 'w') as routes:
            print("""<routes>
            <vType id="standard_car" length="3.0" maxSpeed="15" minGap="1.0" accel="1.0" decel="4.0" />
            <route id="N_S" edges="gneE5 gneE1 -gneE3 -gneE7"/>
            <route id="N_E" edges="gneE5 gneE1 -gneE0 -gneE4"/>
            <route id="N_W" edges="gneE5 gneE1 -gneE2 -gneE6"/>
            <route id="S_W" edges="gneE7 gneE3 -gneE2 -gneE6"/>
            <route id="S_E" edges="gneE7 gneE3 -gneE0 -gneE4"/>
            <route id="S_N" edges="gneE7 gneE3 -gneE1 -gneE5"/>

            <route id="W_E" edges="gneE6 gneE2 -gneE0 -gneE4"/>
            <route id="W_N" edges="gneE6 gneE2 -gneE1 -gneE5"/>
            <route id="W_S" edges="gneE6 gneE2 -gneE3 -gneE7"/>
            <route id="E_N" edges="gneE4 gneE0 -gneE1 -gneE5"/>
            <route id="E_S" edges="gneE4 gneE0 -gneE3 -gneE7"/>
            <route id="E_W" edges="gneE4 gneE0 -gneE2 -gneE6"/>
            """, file=routes)
            car_counter = -1
            for step in range(len(v_schedule)):
                # print(v_schedule[step])
                for j in range(len(v_schedule[step])):  # 遍历每个出发点
                    car_counter += 1
                    origin = v_schedule[step][j]  # 就是出发点
                    straight_or_turn = np.random.uniform()  # 生成一个01随机数 判断是直行还是左转
                    if straight_or_turn < self.idealStraight * 0.1:

                        if origin == 'gneE6':  # 根据出发点生成路线
                            print(
                                "    <vehicle id='W_E_%i' type='standard_car' route='W_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE4':
                            print(
                                "    <vehicle id='E_W_%i' type='standard_car' route='E_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE5':
                            print(
                                "    <vehicle id='N_S_%i' type='standard_car' route='N_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        else:
                            print(
                                "    <vehicle id='S_N_%i' type='standard_car' route='S_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                    elif straight_or_turn < self.idealLeft * 0.1:  # 25%左转
                        if origin == 'gneE7':
                            print(
                                "    <vehicle id='S_W_%i' type='standard_car' route='S_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE6':
                            print(
                                "    <vehicle id='W_N_%i' type='standard_car' route='W_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE5':
                            print(
                                "    <vehicle id='N_E_%i' type='standard_car' route='N_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE4':
                            print(
                                "    <vehicle id='E_S_%i' type='standard_car' route='E_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                    else:  # 剩余右转
                        if origin == 'gneE7':
                            print(
                                "    <vehicle id='S_E_%i' type='standard_car' route='S_E' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE6':
                            print(
                                "    <vehicle id='W_S_%i' type='standard_car' route='W_S' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE5':
                            print(
                                "    <vehicle id='N_W_%i' type='standard_car' route='N_W' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
                        elif origin == 'gneE4':
                            print(
                                "    <vehicle id='E_N_%i' type='standard_car' route='E_N' depart='%s' departLane='random' departSpeed='10' />" % (
                                    car_counter, float(step)), file=routes)
            print("</routes>", file=routes)
        self.totalNumber = car_counter
        # print(self.totalNumber)
        self.update_info()

    def get_car_number(self):
        return self.totalNumber

    def update_info(self):
        pass
if __name__ == '__main__':
    totalNumber, maxSteps, leftTurn, straight, fileName,scale = 4000,3600*2,4,4,"./sumoNet/test4.rou.xml",1
    gencar = GenCar(totalNumber, maxSteps, leftTurn, straight, fileName,scale)
    gencar.generate_routefile()
    print(gencar.totalNumber)

#每次生成一个车辆分布图