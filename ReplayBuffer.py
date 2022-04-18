import random
from collections import namedtuple,deque

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward', 'mask'))  # 命名元组

class ReplayBuffer:
    def __init__(self,capacity,minibatch):
        self.memory = deque([],maxlen=capacity)
        self.capacity = capacity
        self.minibatch = minibatch
        self.position = 0

    def append_buffer(self,*args):
        # new_m = Transition(*args)
        # now_c = self.get_size()
        # if now_c >= self.capacity:
        #     self.memory.pop(0)
        # else:
        #     self.memory.append(None)
        #     self.memory[self.position] = new_m
        #     self.position = (self.position + 1) % self.capacity
        #     if None in self.memory:
        #         self.memory.remove(None)
        self.memory.append(Transition(*args))

    def get_size(self):
        return len(self.memory)

    def sample(self):
        trajs = random.sample(self.memory, self.minibatch)
        return trajs