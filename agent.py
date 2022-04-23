from net import QNet
import numpy as np
import random
import torch
import torch.optim as optim
from datetime import datetime
from collections import namedtuple

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'mask'))  # 命名元组

class Agent():
    def __init__(self,in_dim,mid_dim,out_dim,learning_rate, gamma, epsilon, alpha):
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.alpha = alpha

        self.in_dim = in_dim
        self.mid_dim = mid_dim
        self.out_dim = out_dim

        self.cri = QNet(in_dim, mid_dim, out_dim)
        self.cri_target = QNet(in_dim, mid_dim, out_dim)
        self.act = QNet(in_dim, mid_dim, out_dim)

    def save_model(self):
        # 保存模型
        file_name = "model-{0}.pt".format(datetime.now().strftime("%F-%H-%M-%S"))
        torch.save(self.cri.state_dict(), './model/{0}'.format(file_name))
        return file_name

class DQNAgent():
    def __init__(self, in_dim, mid_dim, out_dim, replayBuffer, learning_rate, gamma, epsilon, alpha, sumoAgent, p=False):

        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.alpha = alpha

        self.in_dim = in_dim
        self.mid_dim = mid_dim
        self.out_dim = out_dim

        self.cri = QNet(in_dim, mid_dim, out_dim)
        self.cri_target = QNet(in_dim, mid_dim, out_dim)
        self.act = QNet(in_dim, mid_dim, out_dim)

        self.sumoAgent = sumoAgent  # ??
        self.replayBuffer = replayBuffer
        self.optimizer = optim.Adam(self.cri.parameters(), lr=self.learning_rate)  # 学习率优化器

        self.criterion = torch.nn.SmoothL1Loss()
        self.soft_update_tau = 2 ** -8
        self.k = 0.8
        self.ra = 0.9
        self.priority_memory = p
        self.loss = 0 # 暂存loss

    def get_state(self, *args):
        return self.sumoAgent.get_observation(*args)

    def select_action(self, state):
        self.epsilon = max(self.epsilon * 0.9, 0.1)  # 约探索288轮

        # 随机产生一个数据
        if np.random.rand() <= self.epsilon:
            a = random.randrange(self.out_dim)
            # print('1 a',a)
            return a
        else:
            with torch.no_grad():
                action = self.cri(state)  # 使用当前q网络计算四个动作对应的q值
            a = int(action.argmax(dim=1)[0])
            # print("网络拟合数据", action)
            # print("网络选取动作", a)
            return a  # 返回q值最大的那个

    def select_action_biu(self, state,flag):
        self.epsilon = max(self.epsilon * 0.9, 0.1)  # 约探索288轮

        # 随机产生一个数据

        if np.random.rand() <= self.epsilon:
            if flag == 1:
                a = random.randrange(self.out_dim//2)
            else:
                a = random.randrange(self.out_dim)
            # print('1 a',a)
            return a
        else:
            with torch.no_grad():
                action = self.cri(state)  # 使用当前q网络计算四个动作对应的q值
            if flag == 1:
                for i in range(4, 8):
                    action[i] = -np.inf
            a = int(action.argmax(dim=1)[0])
            # print("网络拟合数据", action)
            # print("网络选取动作", a)
            return a  # 返回q值最大的那个

    def take_action(self, current_action, max_step):  # 执行新动作
        # 返回当前动作执行后的waiting_time queue delay等等指标
        if current_action == 0 or current_action == 2:
            n_step = 30
        else:
            n_step = 5
        next_obs, r = self.sumoAgent.step(current_action, n_step)  # 传入动作和执行的步数
        if self.sumoAgent.get_current_time() < max_step:
            done = False
        else:
            done = True

        return next_obs, r, done

    def take_action_biu(self, current_action, max_step):  # 执行新动作
        # 返回当前动作执行后的waiting_time queue delay等等指标
        n_step = 30
        next_obs, r = self.sumoAgent.step(current_action, n_step)  # 传入动作和执行的步数
        if self.sumoAgent.get_current_time() < max_step:
            done = False
        else:
            done = True

        return next_obs, r, done


    def optimize_model(self):
        if self.replayBuffer.get_size() < self.replayBuffer.minibatch:
            return

        transitions = self.replayBuffer.sample()

        # 先处理好states,next_states,reward,mask
        batch = Transition(*zip(*transitions))
        q_label = []
        for i in range(len(batch.state)):
            state = torch.as_tensor(batch.state[i], dtype=torch.float)
            next_state = torch.as_tensor(batch.next_state[i], dtype=torch.float)
            action = batch.action[i]
            mask = 1 if batch.mask[i] == False else 0
            reward = batch.reward[i]
            # print('action ',action)
            # print("self.cri(state)[0][action] ",self.cri(state)[0][action])
            state_value = self.cri(state)[0][action]
            # print('state_value:',state_value)

            next_state_value = self.cri_target(next_state).max(0)[0]
            # print('next_state_value:',next_state_value)

            ql = state_value + mask * self.gamma * (reward + next_state_value - state_value)
            q_label.append(ql)
        # print("q_label:",q_label)
        q_label = torch.cat([ql.unsqueeze(0) for ql in q_label], 0)
        # 计算损失
        q_list = []
        if self.priority_memory:
            for i in range(len(batch.state)):
                state = batch.state[i]
                action = batch.action[i]
                q = self.cri(state)[0][action]
                q_list.append(q)
        else:
            for i in range(len(batch.state)):
                state = batch.state[i]
                action = batch.action[i]
                q = self.cri(state)[0][action]
                q_list.append(q)

        q_list = torch.cat([q1.unsqueeze(0) for q1 in q_list], 0)
        # print("q_list ",q_list)
        # print("len q_list ", len(q_list))
        # print('q_label', q_label)
        # print('len q_label', len(q_label))
        self.loss = self.criterion(q_list, q_label)
        self.optim_update(self.loss)

    def optim_update(self, loss):
        self.optimizer.zero_grad()
        loss.requires_grad_(True)
        loss.backward()
        # for param in self.cri.parameters():
        #     param.grad.data.clamp_(-10, 10)
        self.optimizer.step()
        return loss.item()

    def optimize_target_model(self):  # soft_update target_model  暂时不用
        for tar, cur in zip(self.cri_target.parameters(), self.cri.parameters()):
            tar.data.copy_(cur.data * self.soft_update_tau + cur.data * (1 - self.soft_update_tau))

    def save_model(self):
        # 保存模型
        file_name = "model-{0}.pt".format(datetime.now().strftime("%F-%H-%M-%S"))
        torch.save(self.cri.state_dict(), './model/{0}'.format(file_name))
        return file_name

    def checkpoint(self,episode):
        path = "checkpoint-{0}.pt".format(datetime.now().strftime("%F-%H-%M-%S"))
        torch.save({
            'epoch':episode,
            'cri_model_state_dict':self.cri.state_dict(),
            'cri_target_model_state_dict': self.cri_target.state_dict(),
            'act_model_state_dict': self.act.state_dict(),
            'optimizer_state_dict':self.optimizer.state_dict(),
            'loss':self.loss
        }, path)

    def load_model(self,path):
        self.cri.load_state_dict(torch.load(path))
