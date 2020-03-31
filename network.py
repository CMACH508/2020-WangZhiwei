import hex
import torch.nn as nn
import torch
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
import numpy as np

class ResBlock(nn.Module):
    def __init__(self):
        super(ResBlock, self).__init__()
        self.conv1 = self.conv(relu=True)
        self.conv2 = self.conv(relu=False)
        self.relu = nn.ReLU()

    def conv(self, relu):
        layers = []
        layers.append(nn.Conv2d(32, 32, 3, 1, padding=1))
        layers.append(nn.BatchNorm2d(32))
        if relu:
            layers.append(nn.ReLU())

        layers = nn.ModuleList(layers)
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out += x
        out = self.relu(out)
        return out

class Resnet(nn.Module):
    def __init__(self):
        super(Resnet, self).__init__()
        self.blocks = []
        for _ in range(10):
            self.blocks.append(ResBlock())
        self.blocks = nn.ModuleList(self.blocks)
        self.resnet = nn.Sequential(*self.blocks)

    def forward(self, x):
        return self.resnet(x)

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.head = self.conv(in_channels=4, out_channels=32)
        self.resnet = Resnet()
        self.policy_conv = self.conv(in_channels=32, out_channels=1, kernel_size=1)
        self.logsoftmax = nn.LogSoftmax(dim=1)
        self.value_conv = self.conv(in_channels=32, out_channels=1, kernel_size=1)
        self.value_fc = nn.Linear(hex.SIZE * hex.SIZE, 1)
        self.tanh = nn.Tanh()

    def conv(self, in_channels, out_channels, kernel_size=3, relu=True):
        layers = []
        layers.append(nn.Conv2d(in_channels=in_channels, out_channels=out_channels,
                                kernel_size=kernel_size, padding=0))
        layers.append(nn.BatchNorm2d(out_channels))
        if relu:
            layers.append(nn.ReLU())
        layers = nn.ModuleList(layers)
        return nn.Sequential(*layers)

    def forward(self, feature):
        x = self.head(feature)
        x = self.resnet(x)

        logpolicy = self.policy_conv(x)
        logpolicy = self.logsoftmax(logpolicy.view(-1, hex.SIZE * hex.SIZE))

        #print("before conv", x.shape)
        value = self.value_conv(x)
        value = self.value_fc(value.view(-1, hex.SIZE * hex.SIZE))
        value = self.tanh(value)

        return logpolicy, value

class PV():
    def __init__(self, model_path=None, num=0):
        self.net = Network()
        self.net.cuda(num)
        self.num = num
        #self.net = torch.nn.DataParallel(self.net, device_ids=[num])
        cudnn.benchmark = True
        if model_path is not None:
            loc1 = 'cuda:0'
            loc2 = 'cuda:' + str(num)
            self.net.load_state_dict(torch.load(model_path, map_location={loc1:loc2}))
        self.net.eval()

    def run(self, board):
        probs, values = self.run_many([board])
        return probs[0], values[0]

    def run_many(self, boards):
        fs = [board.to_feature() for board in boards]
        fs = np.array(fs, dtype=np.float32)
        fs = torch.FloatTensor(fs)
        log_act_probs, value = self.net(Variable(fs.cuda(self.num)))
        act_probs = np.exp(log_act_probs.data.cpu().numpy())
        value = value.data.cpu().numpy()

        return act_probs, value
