import hex
import network
import numpy as np
import mcts
import rave
import random
import os
from multiprocessing import Process
import multiprocessing
import time
import torch
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--saved_model', default=None, type=str)
parser.add_argument('--use_cuda', default=True, type=bool)
parser.add_argument('--game_num', default=50, type=int)
parser.add_argument('--batch_size', default=1024, type=int)
parser.add_argument('--lr', default=0.0001, type=float)
parser.add_argument('--l2', default=0.00001, type=float)
parser.add_argument('--mode', default='train', type=str)
parser.add_argument('--parallel_num', default=10, type=int)
parser.add_argument('--seed', default=10, type=int)
parser.add_argument('--logfile-name', default='aa', type=str)
args = parser.parse_args()

openings = random.sample([i for i in range(hex.SIZE * hex.SIZE)], args.game_num)

class GreedyPlayer:
    def __init__(self, net, board=None):
        self.net = net
        if board is None:
            board = hex.Hex()
        self.board = board

    def get_move(self):
        probs, _ = self.net.run(self.board)
        for i in range(len(probs)):
            if not self.board.is_move_legal(i // hex.SIZE, i % hex.SIZE):
                probs[i] = 0
        move = np.argmax(probs)
        return move // hex.SIZE, move % hex.SIZE

    def make_move(self, x, y):
        self.board = self.board.move(x, y)

class MCTSPlayer:
    def __init__(self, net, simulations_per_move=800, resign_threshold=-1.0, num_parallel=2, th=10, cpuct=1.5):
        self.net = net
        self.simulations_per_move = simulations_per_move
        self.temp_threshold = th
        self.num_parallel = num_parallel
        self.cpuct = cpuct
        self.qs = []
        self.comments = []
        self.searches_pi = []
        self.root = None
        self.result = 0
        self.result_string = None
        self.resign_threshold = -abs(resign_threshold)
        super().__init__()

    def initialize_game(self, board=None):
        if board is None:
            board = hex.Hex()
        self.board = board
        self.root = mcts.MCTSNode(board, cpuct=self.cpuct)
        self.result = 0
        self.result_string = None
        self.comments = []
        self.searches_pi = []
        self.qs = []
        first_node = self.root.select_leaf()
        prob, val = self.net.run(first_node.board)
        first_node.incorporate_results(prob, val, first_node)

    def set_size(self, n=hex.SIZE):
        self.size = n
        self.clear()

    def clear(self):
        self.board = hex.Hex()

    def should_resign(self):
        return self.root.Q_perspective < self.resign_threshold

    def tree_search(self):
        leaves = []
        failsafe = 0
        while len(leaves) < self.num_parallel and failsafe < self.num_parallel * 2:
            failsafe += 1
            leaf = self.root.select_leaf()

            if leaf.is_done():
                value = leaf.board.winner
                leaf.backup_value(value, up_to=self.root)
                continue
            leaf.add_virtual_loss(up_to=self.root)
            leaves.append(leaf)
        if leaves:
            move_probs, values = self.net.run_many(
                [leaf.board for leaf in leaves])

            for leaf, move_prob, value in zip(leaves, move_probs, values):
                leaf.revert_virtual_loss(up_to=self.root)
                leaf.incorporate_results(move_prob, value, up_to=self.root)

    def get_move(self):
        if self.board.is_game_over():
            return hex.SIZE, hex.SIZE
        if self.should_resign():
            return hex.SIZE, hex.SIZE

        for i in range(hex.SIZE * hex.SIZE):
            x = i // hex.SIZE
            y = i % hex.SIZE
            if self.root.board.is_move_legal(x, y):
                new_board = self.root.board.move(x, y)
                if new_board.winner == self.root.board.to_play:
                    self.root.child_N[i] = 100000
                    return x, y

        current_readouts = self.root.N
        while self.root.N < current_readouts + self.simulations_per_move:
            self.tree_search()

        #print(self.root.Q_perspective)

        if self.root.board.step > self.temp_threshold:
            move = np.argmax(self.root.child_N)
        else:
            cdf = self.root.child_N.cumsum()
            cdf /= cdf[-1]
            selection = random.random()
            move = cdf.searchsorted(selection)
            assert self.root.child_N[move] != 0

        return move // hex.SIZE, move % hex.SIZE

    def make_move(self, x, y):
        self.qs.append(self.root.Q)

        try:
            #print("make: ", x, y)
            if x == hex.SIZE and y == hex.SIZE:
                self.root.board = self.root.board.move(x, y)
                self.board = self.root.board
                return True
            self.root = self.root.maybe_add_child(x * hex.SIZE + y)

        except:
            print("Illegal move")
            self.qs.pop()
            return False
        self.board = self.root.board  # for showboard
        del self.root.parent.children
        return True

    def is_game_over(self):
        over = self.board.is_game_over()
        return over, self.board.winner

    def show_board(self):
        print(self.board)

class RAVEPlayer:
    def __init__(self, net, simulations_per_move=800, resign_threshold=-0.8, num_parallel=2, th=10, cpuct=1.5):
        self.net = net
        self.simulations_per_move = simulations_per_move
        self.temp_threshold = th
        self.num_parallel = num_parallel
        self.cpuct = cpuct
        self.qs = []
        self.comments = []
        self.searches_pi = []
        self.root = None
        self.result = 0
        self.result_string = None
        self.resign_threshold = -abs(resign_threshold)
        super().__init__()

    def initialize_game(self, board=None):
        if board is None:
            board = hex.Hex()
        self.board = board
        self.root = rave.MCTSNode(board)
        self.result = 0
        self.result_string = None
        self.comments = []
        self.searches_pi = []
        self.qs = []
        first_node = self.root.select_leaf()
        prob, val = self.net.run(first_node.board)
        first_node.incorporate_results(prob, val, first_node)

    def set_size(self, n=13):
        self.size = n
        self.clear()

    def clear(self):
        self.board = hex.Hex()

    def should_resign(self):
        return self.root.Q_perspective < self.resign_threshold

    def tree_search(self):
        leaves = []
        failsafe = 0
        while len(leaves) < self.num_parallel and failsafe < self.num_parallel * 2:
            failsafe += 1
            leaf = self.root.select_leaf()

            if leaf.is_done():
                value = leaf.board.winner
                leaf.backup_value(value, up_to=self.root)
                continue
            leaf.add_virtual_loss(up_to=self.root)
            leaves.append(leaf)
        if leaves:
            move_probs, values = self.net.run_many(
                [leaf.board for leaf in leaves])

            for leaf, move_prob, value in zip(leaves, move_probs, values):
                leaf.revert_virtual_loss(up_to=self.root)
                leaf.incorporate_results(move_prob, value, up_to=self.root)

    def get_move(self):
        if self.board.is_game_over():
            return hex.SIZE, hex.SIZE
        if self.should_resign():
            return hex.SIZE, hex.SIZE

        current_readouts = self.root.N
        while self.root.N < current_readouts + self.simulations_per_move:
            self.tree_search()

        #print(self.root.Q_perspective)

        if self.root.board.step > self.temp_threshold:
            move = np.argmax(self.root.child_N)
        else:
            cdf = self.root.child_N.cumsum()
            cdf /= cdf[-1]
            selection = random.random()
            move = cdf.searchsorted(selection)
            assert self.root.child_N[move] != 0

        return move // hex.SIZE, move % hex.SIZE

    def make_move(self, x, y):
        self.qs.append(self.root.Q)

        try:
            #print("make: ", x, y)
            if x == hex.SIZE and y == hex.SIZE:
                self.root.board = self.root.board.move(x, y)
                self.board = self.root.board
                return True
            self.root = self.root.maybe_add_child(x * hex.SIZE + y)

        except:
            print("Illegal move")
            self.qs.pop()
            return False
        self.board = self.root.board  # for showboard
        del self.root.parent.children
        return True

    def is_game_over(self):
        over = self.board.is_game_over()
        return over, self.board.winner

    def show_board(self):
        print(self.board)


def single_play(net1, net2, game, simulation, old_winning, flag):
    print("flag:", flag)
    parallel_num = args.parallel_num

    for i in range(args.game_num // parallel_num):

        show = False
        if game == 0:
            show = True
        print("Game:", game + i)
        player1 = MCTSPlayer(net=net1, simulations_per_move=simulation, th=0, resign_threshold=-1.0)
        player2 = MCTSPlayer(net=net2, simulations_per_move=simulation, th=0, resign_threshold=-1.0)
        player1.initialize_game()
        player2.initialize_game()
        player1.make_move(openings[game + i] // hex.SIZE, openings[game + i] % hex.SIZE)
        player2.make_move(openings[game + i] // hex.SIZE, openings[game + i] % hex.SIZE)
        color = hex.WHITE

        while not player1.board.is_game_over():
            if color == flag:
                x, y = player1.get_move()
            else:
                x, y = player2.get_move()
            color = -color
            player1.make_move(x, y)
            player2.make_move(x, y)
            if show:
                print(player1.board)

        winner = player1.board.winner
        if winner == flag:
            old_winning.append(1)

        if show:
            print(player1.board, player1.board.step)
            print("winner:", ".XO"[winner])

def write_pgn(old_name, new_name, new_white, new_black):
    f = open('wbec.pgn', 'a')

    white = old_name
    black = new_name
    whitewins = args.game_num - new_black  # old model is white
    for _ in range(args.game_num):
        f.write("[Event \"F/S\"]\n")
        f.write("[Site \"Belgrade\"]\n")
        f.write("[Date \"1992\"]\n")
        f.write("[Round \"29\"]\n")
        f.write("[White \"" + white + "\"]\n")
        f.write("[Black \"" + black + "\"]\n")
        if whitewins > 0:
            r = '1-0'
        else:
            r = '0-1'
        f.write("[Result \"" + r + "\"]\n")
        f.write('\n')
        f.write('1. ' + r + '\n')
        whitewins -= 1

    white, black = black, white
    whitewins = new_white  # new model is white
    for _ in range(args.game_num):
        f.write("[Event \"F/S\"]\n")
        f.write("[Site \"Belgrade\"]\n")
        f.write("[Date \"1992\"]\n")
        f.write("[Round \"29\"]\n")
        f.write("[White \"" + white + "\"]\n")
        f.write("[Black \"" + black + "\"]\n")
        if whitewins > 0:
            r = '1-0'
        else:
            r = '0-1'
        f.write("[Result \"" + r + "\"]\n")
        f.write('\n')
        f.write('1. ' + r + '\n')
        whitewins -= 1

    f.close()

if __name__ == '__main__':
    game_num = args.game_num

    multiprocessing.set_start_method('spawn')
    starttime = time.time()
    parallel = args.parallel_num
    pc1name = 'best.model'
    pc2name = args.saved_model

    nets1 = []
    nets2 = []
    for i in range(parallel):
        nets1.append(network.PV(pc1name, num=i%2))
        nets2.append(network.PV(pc2name, num=i%2))

    l = []
    old = 0
    whitewins = 0
    blackwins = 0

    flag = hex.BLACK

    with multiprocessing.Manager() as mg:
        winning_list = multiprocessing.Manager().list([])
        jobs = [Process(target=single_play,
                    args=(nets1[i], nets2[i], i * game_num // parallel, 1600, winning_list, flag)) for i in range(parallel)]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()

        whitewins = args.game_num - len(winning_list)

        flag = -flag
        jobs = [Process(target=single_play,
                    args=(nets1[i], nets2[i], i * game_num // parallel, 1600, winning_list, flag)) for i in range(parallel)]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()

        old = len(winning_list)
        blackwins = 2 * args.game_num - old - whitewins
        print("old wins", len(winning_list))

    f = open('best.txt', 'r')
    old_name = f.readline().strip()
    f.close()
    write_pgn(old_name, pc2name, whitewins, blackwins)

    line = ''
    if old < game_num:
        g = open('best.txt', 'w')
        g.write(pc2name)
        g.close()
        shutil.copy(pc2name, 'best.model')
        line += '*'

    line += 'best vs ' + pc2name + ' = ' + str(old) + ':' + str(2 * game_num - old)
    f = open('elo.txt', 'a')
    f.write(line + '\n')
    f.close()



    endtime = time.time()
    print("takes", (endtime - starttime) / 60, "minutes")
