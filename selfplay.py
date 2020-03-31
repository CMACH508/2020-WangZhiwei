import random
import datetime
import argparse
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from torch.autograd import Variable
from collections import defaultdict, deque
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
import network
import mcts
import math
import sys
import play
import hex
from multiprocessing import Process
from multiprocessing import Pool, Manager
import multiprocessing
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('--saved_model', default=None, type=str)
parser.add_argument('--use_cuda', default=True, type=bool)
parser.add_argument('--game_num', default=20000, type=int)
parser.add_argument('--batch_size', default=128, type=int)
parser.add_argument('--lr', default=0.01, type=float)
parser.add_argument('--parallel_num', default=30, type=int)
args = parser.parse_args()

SIZE = hex.SIZE

def augment(board, pi):
    rd = random.random()
    if rd < 0.5:
        board_save = np.rot90(board, k=2, axes=(1, 2))
        pi_save = np.reshape(pi, (hex.SIZE, hex.SIZE))
        pi_save = np.rot90(pi_save, k=2)
        pi_save = pi_save.reshape(hex.SIZE * hex.SIZE)
        return board_save, pi_save

    return board, pi

def single_play(num, game, simulation):
    for i in range(args.game_num // args.parallel_num):
        while True:
            if os.path.exists('ok.txt'):
                break
            else:
                time.sleep(1)
        model_path = None
        if os.path.exists('current.model'):
            model_path = 'current.model'
        net = network.PV(model_path, num=num)
        show = False
        if game == 0:
            show = True
        #print("Game:", game + i)
        player = play.MCTSPlayer(net=net, simulations_per_move=simulation, th=10)

        if random.random() < 0.05:
            player.resign_threshold = -1.0
        player.initialize_game()

        rd = random.randint(0, hex.SIZE ** 2 - 1)
        player.make_move(rd // hex.SIZE, rd % hex.SIZE)
        player.root.inject_noise()

        features = []
        pis = []
        outcomes = []
        while not player.board.is_game_over():
            x, y = player.get_move()
            if False:
                print(player.board)
            if x != SIZE or y != SIZE:
                pi = player.root.children_as_pi()
                feature, pi_save = augment(player.board.to_feature(), pi)
                if False:
                    print(pi)
                    print(np.argmax(pi) // 13, np.argmax(pi) % 13)
                features.append(feature)
                pis.append(pi_save)
                #pis.append(x * SIZE + y)
            player.make_move(x, y)
        winner = player.board.winner
        if show:
            p = ".XO"
            print("len", len(pis))
            print(p[winner], "wins")
        for _ in range(player.board.step):
            outcomes.append(winner)

        train_data = []
        for feature, pi, z in zip(features, pis, outcomes):
            train_data.append((feature, pi, z))
        train_data = np.array(train_data)
        now_time = datetime.datetime.now()
        ts = datetime.datetime.strftime(now_time, '%Y-%m-%d-%H%M%S')
        rd = random.randint(0, 100000000)
        filename = './data/'
        filename += ts + '-' + str(rd) + '.npy'
        np.save(filename, train_data)
        #print(filename, 'ok')

def selfplay():
    '''model_path = None 
    nets = []
    for i in range(args.parallel_num):
        nets.append(network.PV(model_path, num=i % torch.cuda.device_count()))'''

    jobs = [Process(target=single_play, args=(i%torch.cuda.device_count(), i * args.game_num // args.parallel_num, 400)) for i in range(args.parallel_num)]
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    selfplay()
