# 定义带有卷积层的神经网络
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict


class QNet(nn.Module):
    def __init__(self, in_dim, mid_dim, out_dim):
        '''
        初始化神经网络
        :param in_dim:
        :param mid_dim:
        :param out_dim:
        '''
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 60)
        self.fc3 = nn.Linear(60, 4)

    def forward(self, state):
        state = F.max_pool2d(F.relu(self.conv1(state)), (2, 2))
        state = F.max_pool2d(F.relu(self.conv2(state)), (2, 2))
        state = state.view()
        state = F.relu(self.fc1(state))
        state = F.relu(self.fc2(state))
        state = self.fc3(state)
        return state


class QNetDuel(nn.Module):
    def __init__(self, in_dim, mid_dim, out_dim):
        '''
        初始化神经网络
        :param in_dim:
        :param mid_dim:
        :param out_dim:
        '''

        super().__init__()
        self.net_state = nn.Sequential(
            OrderedDict(
                [
                    ("conv1", nn.Conv2d(in_dim, in_dim * 2)),
                    ("relu1", nn.ReLU()),
                    ("conv2", nn.Conv2d(in_dim, in_dim * 2)),
                    ("relu1", nn.ReLU()),
                ]
            )
        )
        self.net_adv = nn.Sequential(
            OrderedDict([
                ("dense1",nn.Linear())
            ])
        )

    def forward(self, state):
        state = F.max_pool2d(F.relu(self.conv1(state)), (2, 2))
        state = F.max_pool2d(F.relu(self.conv2(state)), (2, 2))
        state = state.view()
        state = F.relu(self.fc1(state))
        state = F.relu(self.fc2(state))
        state = self.fc3(state)
        return state
