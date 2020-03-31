import torch
import numpy as np
import argparse
import hex
import network
import torch.nn.functional as F
import torch.optim as optim
import torch.backends.cudnn as cudnn
from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable
import os

parser = argparse.ArgumentParser()
parser.add_argument('--saved_model', default=None, type=str)
parser.add_argument('--use_cuda', default=True, type=bool)
parser.add_argument('--pc', default=False, type=bool)
parser.add_argument('--game_num', default=500, type=int)
parser.add_argument('--batch_size', default=128, type=int)
parser.add_argument('--lr', default=0.0001, type=float)
parser.add_argument('--l2', default=0.00001, type=float)
parser.add_argument('--mode', default='train', type=str)
parser.add_argument('--parallel_num', default=5, type=int)
args = parser.parse_args()

def _one_hot(index):
    onehot = np.zeros([hex.SIZE * hex.SIZE], dtype=np.float32)
    onehot[index] = 1
    return onehot

class HexDataset(Dataset):
    def __init__(self, path):
        self.data = np.load(path, allow_pickle=True)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        position = np.array(self.data[idx][0], dtype=np.float32)
        if type(self.data[idx][1]) == np.ndarray:
            pi = np.array(self.data[idx][1], dtype=np.float32)
        else:
            pi = _one_hot(self.data[idx][1])
        result = self.data[idx][2]
        return torch.FloatTensor(position), torch.FloatTensor(pi), torch.FloatTensor([result])

class PcDataset(Dataset):
    def __init__(self, path):
        self.data = np.load(path, allow_pickle=True)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        position = np.array(self.data[idx][0], dtype=np.float32)
        aver = self.data[idx][2]
        return torch.FloatTensor(position), torch.FloatTensor([aver])

def consistency(net):
    optimizer = optim.SGD(net.parameters(), weight_decay=args.l2, lr=args.lr, momentum=0.9)
    #optimizer = optim.Adam(net.parameters(), lr=args.lr, weight_decay=args.l2)
    net.train()
    training_data = HexDataset('consistency.npy')
    dataloader = DataLoader(training_data, batch_size=args.batch_size,
                            shuffle=True, num_workers=8)
    
    for idx, (position_batch, aver_batch) in enumerate(dataloader):

        if args.use_cuda:
            position_batch = Variable(torch.FloatTensor(position_batch).cuda())
            aver_batch = Variable(torch.FloatTensor(aver_batch).cuda())
        else:
            position_batch = Variable(torch.FloatTensor(position_batch))
            aver_batch = Variable(torch.FloatTensor(aver_batch))

        optimizer.zero_grad()

        # forward
        policy, value = net(position_batch)

        value_loss = F.mse_loss(value.view(-1), aver_batch.view(-1))
        loss = value_loss
        loss.backward()
        optimizer.step()

        mse = value_loss.data.item()

        fmse = open('pc.txt', 'a')
        fmse.write(str(mse) + '\n')
        fmse.close()

        if i % (args.batch_size * 1000) == 0:
            model_name = 'current.model'
            torch.save(net.state_dict(), model_name)

        i += args.batch_size

    model_name = 'current.model'
    torch.save(net.state_dict(), model_name)

def train(net):
    optimizer = optim.SGD(net.parameters(), weight_decay=args.l2, lr=args.lr, momentum=0.9)
    #optimizer = optim.Adam(net.parameters(), lr=args.lr, weight_decay=args.l2)
    net.train()

    training_data = HexDataset('games.npy')
    dataloader = DataLoader(training_data, batch_size=args.batch_size,
                            shuffle=True, num_workers=8)
    print("training")
    i = 0

    for idx, (position_batch, pi_batch, result_batch) in enumerate(dataloader):
        # print(position_batch)

        if args.use_cuda:
            position_batch = Variable(torch.FloatTensor(position_batch).cuda())
            pi_batch = Variable(torch.FloatTensor(pi_batch).cuda())
            result_batch = Variable(torch.FloatTensor(result_batch).cuda())
        else:
            position_batch = Variable(torch.FloatTensor(position_batch))
            pi_batch = Variable(torch.FloatTensor(pi_batch))
            result_batch = Variable(torch.FloatTensor(result_batch))

        optimizer.zero_grad()

        # forward
        policy, value = net(position_batch)

        value_loss = F.mse_loss(value.view(-1), result_batch.view(-1))
        policy_loss = -torch.mean(torch.sum(pi_batch * policy, 1))
        loss = value_loss + policy_loss
        loss.backward()
        optimizer.step()

        mse = value_loss.data.item()
        ce = policy_loss.data.item()
        #print("ce:", ce)
        #print("mse:", mse)

        fmse = open('mse.txt', 'a')
        facc = open('ce.txt', 'a')
        fmse.write(str(mse) + '\n')
        facc.write(str(ce) + '\n')
        fmse.close()
        facc.close()

        if i % (args.batch_size * 1000) == 0:
            model_name = 'current.model'
            torch.save(net.state_dict(), model_name)

        i += args.batch_size

    model_name = 'current.model'
    torch.save(net.state_dict(), model_name)

def validate(net):
    net.eval()

    validating_data = HexDataset('9x9validate.npy')
    dataloader = DataLoader(validating_data, batch_size=args.batch_size,
                            shuffle=True, num_workers=8)
    print("validating")

    mean_acc = []
    mean_err = []

    i = 0

    for idx, (position_batch, pi_batch, result_batch) in enumerate(dataloader):
        # print(position_batch)

        if args.use_cuda:
            position_batch = Variable(torch.FloatTensor(position_batch).cuda())
            pi_batch = Variable(torch.FloatTensor(pi_batch).cuda())
            result_batch = Variable(torch.FloatTensor(result_batch).cuda())
        else:
            position_batch = Variable(torch.FloatTensor(position_batch))
            pi_batch = Variable(torch.FloatTensor(pi_batch))
            result_batch = Variable(torch.FloatTensor(result_batch))

        # forward
        output, value = net(position_batch)
        err = F.mse_loss(value.view(-1), result_batch.view(-1)).item()
        output = output.data.cpu().numpy()
        # value = value.data.cpu().numpy()
        output = np.argmax(output, 1)
        # print(output[0])
        pi_batch = pi_batch.data.cpu().numpy()
        pi_batch = np.argmax(pi_batch, 1)
        acc = np.equal(output, pi_batch)
        acc = np.array(acc, np.float32)
        acc = acc.mean()

        #print("acc: ", acc)
        mean_acc.append(acc)
        facc = open('acc.txt', 'a')
        facc.write(str(acc) + '\n')
        facc.close()
        #print("err: ", err)
        mean_err.append(err)
        ferr = open('err.txt', 'a')
        ferr.write(str(err) + '\n')
        ferr.close()

    print("mean acc:", np.average(mean_acc))
    print("mean err:", np.average(mean_err))



if __name__ == '__main__':
    net = network.Network()

    if args.use_cuda:
        net.cuda()
        print("use cuda")
        #net = torch.nn.DataParallel(net, device_ids=range(torch.cuda.device_count()))
        cudnn.benchmark = True

    if args.saved_model is not None and os.path.exists(args.saved_model):
        net.load_state_dict(torch.load(args.saved_model))
    print("load ok")

    if args.mode == 'train':
        for _ in range(1):
            train(net)
            validate(net)
    elif args.mode == 'validate':
        validate(net)
