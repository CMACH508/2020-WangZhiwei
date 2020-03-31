import numpy as np
import copy
from collections import deque

SIZE = 13
BLACK = 1
WHITE = -1
EMPTY = 0

class IllegalMove(Exception):
    pass

class Hex:
    def __init__(self, board=np.zeros(shape=(SIZE, SIZE), dtype=np.int8), winner=EMPTY, to_play=BLACK, step=0):
        self.board = board.copy()
        self.winner = winner
        self.to_play = to_play
        self.step = step

    def is_move_legal(self, x, y):
        return self.board[x][y] == EMPTY

    def reach(self, x, y, target, color):
        mask = np.zeros(shape=(SIZE, SIZE), dtype=np.int8)
        queue = deque()
        queue.append((x, y))
        mask[x][y] = 1
        while len(queue) != 0:
            e = queue.popleft()
            x, y = e[0], e[1]
            if self.board[x][y] == color:
                if color == BLACK and x == target:
                    return True
                elif color == WHITE and y == target:
                    return True

                dx = [0, 0, -1, -1, 1, 1]
                dy = [-1, 1, 0, 1, -1, 0]
                for i in range(6):
                    nx = x + dx[i]
                    ny = y + dy[i]
                    if 0 <= nx and nx < SIZE and 0 <= ny and ny < SIZE \
                            and mask[nx][ny] == 0 and self.board[nx][ny] == color:
                        queue.append((nx, ny))
                        mask[nx][ny] = 1
                
        return False

    def move(self, x, y, color=None):
        pos = copy.deepcopy(self)
        if color == None:
            color = self.to_play
        if x == SIZE and y == SIZE:
            pos.winner = -color
            return pos
        if not pos.is_move_legal(x, y):
            raise IllegalMove("{} move at {} is illegal: \n{}".format(
                "Black" if self.to_play == BLACK else "White", (x, y), self))
        pos.board[x][y] = color
        if pos.reach(x, y, 0, color) and pos.reach(x, y, SIZE - 1, color):
            pos.winner = color
        pos.to_play = -pos.to_play
        pos.step = self.step + 1
        return pos

    def is_game_over(self):
        over = (self.step == SIZE * SIZE or self.winner != EMPTY)
        return over

    def result(self):
        return self.winner

    def __deepcopy__(self, memodict={}):
        new_board = np.copy(self.board)
        return Hex(new_board, self.winner, self.to_play, self.step)

    def all_legal_moves(self):
        ret = []
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i][j] == EMPTY:
                    ret.append(1)
                else:
                    ret.append(0)
        return np.array(ret)

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
                    retstr += 'X'
                elif self.board[i, j] == WHITE:
                    retstr += 'O'
                else:
                    retstr += '.'
                retstr += ' '
            retstr += '\n'
        return retstr

if __name__ == '__main__':
    s = Hex()
    s.move(0, 0)
    s.move(0, 1)
    f = s.to_feature()
    print(f)

'''
# 例如sgf是W+, a1, b2, c3, f4
# 你的程序大概长这样:
first = Hex() # 初始化一个空棋盘

n = 4 # n是这盘棋的步数
moves = [(0, 0), (1, 1), (2, 2), (3, 3)] # 也就是a1, b2, c3, f4
color = BLACK # 黑棋先走
winner = WHITE # 白棋赢了
record = [(first, winner)] # 这是你最后要的结果
while root:
    m = root.m_move.m_point
    first = copy.deepcopy(first)
    first.move(moves[i][0], moves[i][1], color)
    color = -color
    record.append((first, winner))

for r in record:
    print(r[0].board) # 检查一下结果'''
