import numpy


class SumTree:
    write = 0

    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = numpy.zeros(2 * capacity - 1)
        self.data = [0 for i in range(capacity)]

    def _propagate(self, idx, change):  # 前向传播
        parent = (idx - 1) // 2
        self.tree[parent] += change  # p值更新后
        if parent != 0:
            self._propagate(parent, change)  # 递归传递

    def update(self, idx, p):
        change = p - self.tree[idx]
        self.tree[idx] = p
        self._propagate(idx, change)

    def add(self, p, data):

        idx = self.write + self.capacity - 1
        self.data[self.write] = data  # update data_frame
        self.update(idx, p)
        print("到sumTree存入的data", self.data[self.write])

        self.write += 1
        if self.write >= self.capacity:  # 叶节点存满了
            self.write = 0  # 从头开始覆盖优先级小的数据

    def _retrieve(self, idx, s):  # 检索s值
        left = 2 * idx + 1
        right = left + 1
        if left >= len(self.tree):
            return idx

        if s <= self.tree[left]:
            return self._retrieve(left, s)
        else:
            return self._retrieve(right, s - self.tree[left])

    def get(self, s):
        idx = self._retrieve(0, s)
        dataIdx = idx - self.capacity + 1
        return (idx, self.tree[idx], self.data[dataIdx])

    def total(self):
        return self.tree[0]
