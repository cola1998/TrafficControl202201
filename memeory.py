from sumTree import SumTree
from collections import namedtuple, deque
import random

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward', 'mask'))  # 命名元组


class Memory:  # stored as (s,a,r,s_) in SumTree
    e = 0.01
    a = 0.6

    def __init__(self, capacity, minibatch):
        self.tree = SumTree(capacity)
        self.minibatch = minibatch

    def _getPriority(self, error):
        return (error + self.e) ** self.a

    def add(self, error, *args):
        p = self._getPriority(error)
        data = Transition(*args)
        print("sumtree 存入data:", data)
        self.tree.add(p, data)


    def sample(self):
        batch = []  # 存储采样的数据
        segment = self.tree.total() / self.minibatch
        i = 0
        while i <= self.minibatch:
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)

            (idx, p, data) = self.tree.get(s)
            if data != 0:
                print("采样获取data ", data)
                batch.append((idx, data))
                i += 1
        return batch

    def update(self, idx, error):
        p = self._getPriority(error)
        self.tree.update(idx, p)

    def get_size(self):
        return self.tree.write
