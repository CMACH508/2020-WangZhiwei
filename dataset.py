import sys, os
import SgfReader
import numpy as np
import copy
from collections import deque
import random

passlist = []
unpasslist = []
BLACK = 1
WHITE = -1
EMPTY = 0
SIZE = 13

class Hex:
    def __init__(self, board=np.zeros(shape=(SIZE, SIZE), dtype=np.int8), winner=EMPTY, to_play=BLACK):
        self.board = board.copy()
        self.winner = winner
        self.to_play = to_play

    def move(self, x, y, color=None):
        if color == None:
            color = self.to_play
        self.board[x][y] = color
        self.to_play = -self.to_play

    def result(self):
        return self.winner

    def __deepcopy__(self, memodict={}):
        new_board = np.copy(self.board)
        return Hex(new_board, self.winner, self.to_play)

    def to_feature(self):
        ret = np.zeros(shape=(4, SIZE+2, SIZE+2))
        for i in range(SIZE + 2):
            for j in range(SIZE + 2):
                if i == 0 or i == SIZE + 1:
                    if 1 <= j and j <= SIZE:
                        ret[0][i][j] = 1
                elif j == 0 or j == SIZE + 1:
                    if 1 <= i and i <= SIZE:
                        ret[1][i][j] = 1
                else:
                    if self.board[i-1][j-1] == BLACK:
                        ret[0][i][j] = 1
                    elif self.board[i-1][j-1] == WHITE:
                        ret[1][i][j] = 1
                    else:
                        ret[2][i][j] = 1
                if self.to_play == BLACK:
                    ret[3][i][j] = 1
                else:
                    ret[3][i][j] = 0

        return ret

    def __repr__(self):
        retstr = '\n' + ' '
        for i in range(SIZE):
            retstr += chr(ord('a') + i) + ' '
        retstr += '\n'
        for i in range(0, SIZE):
            if i <= 8:
                retstr += ' ' * i + str(i + 1) + ' '
            else:
                retstr += ' ' * (i - 1) + str(i + 1) + ' '
            for j in range(0, SIZE):
                if self.board[i, j] == BLACK:
                    retstr += 'b'
                elif self.board[i, j] == WHITE:
                    retstr += 'w'
                else:
                    retstr += '0'
                retstr += ' '
            retstr += '\n'
        return retstr

def _matrix_onehot(index):
    onehot = np.zeros((SIZE, SIZE))
    onehot[index // SIZE, index % SIZE] = 1
    return onehot

def augment(position, action):
    rd = random.random()
    pi = _matrix_onehot(action)
    policy = action
    if rd < 0.5:
        position = np.rot90(position, k=2, axes=(1, 2))
        pi = np.rot90(pi, k=2)
        pi = pi.reshape(SIZE * SIZE)
        policy = np.argmax(pi)
    return position, policy

num = 0
data_buffer = deque(maxlen=3000000)
for name in os.listdir('all13x13'):
    try:
        f = open('all13x13/' + name, 'r')
        #print(name, ".......")
        num += 1
        if num % 100 == 0:
            print(num)
            print(len(data_buffer))
        reader = SgfReader.SgfReader(f)
        root = reader.getGameTree()
        if root.getSgfProperty('RE') == 'B+':
            winner = BLACK
        elif root.getSgfProperty('RE') == 'W+':
            winner = WHITE
        else:
            print("No winner", name)
            continue
        root = root.m_child
        NoneMoveList = ['invalid', 'resign', 'swap-pieces', 'north', 'east', 'south', 'west']
        board = Hex()
        record = []
        firststep = True
        while root:
            if root.m_move.m_color == SgfReader.HexColor.BLACK:
                assert firststep or color == WHITE, 'there is wrong with color'
                firststep = False
                color = BLACK
            elif root.m_move.m_color == SgfReader.HexColor.WHITE:
                assert firststep or color == BLACK, 'there is wrong with color'
                firststep = False
                color = WHITE
            else:
                assert False, 'there is wrong with color'

            if True:
                action = root.m_move.m_point.x * SIZE + root.m_move.m_point.y  # use int to represent the action in this step
                position, policy = augment(board.to_feature(), action)
                record.append((position, policy, winner))
                board = copy.deepcopy(board)
                board.move(root.m_move.m_point.y, root.m_move.m_point.x, color)
            root = root.m_child

        passlist.append(name)
        data_buffer.extend(record)

    except:
        unpasslist.append(name)

print(len(passlist))
print(len(unpasslist))
data_buffer = random.sample(data_buffer, len(data_buffer))
data_buffer = np.array(data_buffer)
print(data_buffer.shape)
print("shuffle ok")
np.save('game.npy', data_buffer)