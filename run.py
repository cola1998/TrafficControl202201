from memeory import Memory
from SumoAgent import SumoAgent
from genCar import GenCar
from agent import Agent
import torch

def train():
    agent = Agent(4,5,4,0.01,0.99,0.8,0.2)
    model_file_name = agent.save_model()
    return model_file_name
def test(model_file_name):
    model = Agent(4,5,4,0.01,0.99,0.8,0.2)
    path = "./model/{0}".format(model_file_name)
    model.cri.load_state_dict(torch.load(path))


if __name__ == "__main__":
    mode = "train"  # "test
    '''
    mode = train
        1)训练模型，并保存参数
        
    mode = test
        2) 测试模型，重构网络并测试模型
    '''
    train()