# 定义全连接层的神经网络
import torch.nn as nn
from collections import OrderedDict

class QNet(nn.Module):
    def __init__(self,in_dim, mid_dim, out_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, mid_dim),
            nn.ELU(),
            nn.Linear(mid_dim, mid_dim//2),
            nn.ELU(),
            nn.Linear(mid_dim//2, mid_dim//2),
            nn.ELU(),
            nn.Linear(mid_dim//2, out_dim)
        )

    def forward(self, state):
        return self.net(state)