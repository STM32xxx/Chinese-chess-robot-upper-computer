# coding=utf-8

import time, copy
from itertools import count
from collections import namedtuple

from SerialPort import SendString


piece = { 'P': 44, 'N': 108, 'B': 23, 'R': 233, 'A': 23, 'C': 101, 'K': 2500}  # R:車, N:馬, B:相, A:士, K:将, C:炮, P:兵

pst = {
    "P": (
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  9,  9,  9, 11, 13, 11,  9,  9,  9,  0,  0,  0,  0,
      0,  0,  0, 19, 24, 34, 42, 44, 42, 34, 24, 19,  0,  0,  0,  0,
      0,  0,  0, 19, 24, 32, 37, 37, 37, 32, 24, 19,  0,  0,  0,  0,
      0,  0,  0, 19, 23, 27, 29, 30, 29, 27, 23, 19,  0,  0,  0,  0,
      0,  0,  0, 14, 18, 20, 27, 29, 27, 20, 18, 14,  0,  0,  0,  0,
      0,  0,  0,  7,  0, 13,  0, 16,  0, 13,  0,  7,  0,  0,  0,  0,
      0,  0,  0,  7,  0,  7,  0, 15,  0,  7,  0,  7,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  2,  2,  2,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0, 11, 15, 11,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
    ),
    "B":(
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0, 20,  0,  0,  0, 20,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0, 18,  0,  0, 20, 23, 20,  0,  0, 18,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0, 23,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0, 20, 20,  0, 20, 20,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
    ),
    "N": (
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0, 90, 90, 90, 96, 90, 96, 90, 90, 90,  0,  0,  0,  0,
      0,  0,  0, 90, 96,103, 97, 94, 97,103, 96, 90,  0,  0,  0,  0,
      0,  0,  0, 92, 98, 99,103, 99,103, 99, 98, 92,  0,  0,  0,  0,
      0,  0,  0, 93,108,100,107,100,107,100,108, 93,  0,  0,  0,  0,
      0,  0,  0, 90,100, 99,103,104,103, 99,100, 90,  0,  0,  0,  0,
      0,  0,  0, 90, 98,101,102,103,102,101, 98, 90,  0,  0,  0,  0,
      0,  0,  0, 92, 94, 98, 95, 98, 95, 98, 94, 92,  0,  0,  0,  0,
      0,  0,  0, 93, 92, 94, 95, 92, 95, 94, 92, 93,  0,  0,  0,  0,
      0,  0,  0, 85, 90, 92, 93, 78, 93, 92, 90, 85,  0,  0,  0,  0,
      0,  0,  0, 88, 85, 90, 88, 90, 88, 90, 85, 88,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
    ),
    "R": (
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,206,208,207,213,214,213,207,208,206,  0,  0,  0,  0,
      0,  0,  0,206,212,209,216,233,216,209,212,206,  0,  0,  0,  0,
      0,  0,  0,206,208,207,214,216,214,207,208,206,  0,  0,  0,  0,
      0,  0,  0,206,213,213,216,216,216,213,213,206,  0,  0,  0,  0,
      0,  0,  0,208,211,211,214,215,214,211,211,208,  0,  0,  0,  0,
      0,  0,  0,208,212,212,214,215,214,212,212,208,  0,  0,  0,  0,
      0,  0,  0,204,209,204,212,214,212,204,209,204,  0,  0,  0,  0,
      0,  0,  0,198,208,204,212,212,212,204,208,198,  0,  0,  0,  0,
      0,  0,  0,200,208,206,212,200,212,206,208,200,  0,  0,  0,  0,
      0,  0,  0,194,206,204,212,200,212,204,206,194,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
    ),
    "C": (
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,100,100, 96, 91, 90, 91, 96,100,100,  0,  0,  0,  0,
      0,  0,  0, 98, 98, 96, 92, 89, 92, 96, 98, 98,  0,  0,  0,  0,
      0,  0,  0, 97, 97, 96, 91, 92, 91, 96, 97, 97,  0,  0,  0,  0,
      0,  0,  0, 96, 99, 99, 98,100, 98, 99, 99, 96,  0,  0,  0,  0,
      0,  0,  0, 96, 96, 96, 96,100, 96, 96, 96, 96,  0,  0,  0,  0,
      0,  0,  0, 95, 96, 99, 96,100, 96, 99, 96, 95,  0,  0,  0,  0,
      0,  0,  0, 96, 96, 96, 96, 96, 96, 96, 96, 96,  0,  0,  0,  0,
      0,  0,  0, 97, 96,100, 99,101, 99,100, 96, 97,  0,  0,  0,  0,
      0,  0,  0, 96, 97, 98, 98, 98, 98, 98, 97, 96,  0,  0,  0,  0,
      0,  0,  0, 96, 96, 97, 99, 99, 99, 97, 96, 96,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
      0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
    )
}

pst["A"] = pst["B"] # 士和相的子力价值表相同，它们不会移动到同一点
pst["K"] = pst["P"] # 王和兵的子力价值表相同
pst["K"] = [i + piece["K"] if i > 0 else 0 for i in pst["K"]]

A0, I0, A9, I9 = 12 * 16 + 3, 12 * 16 + 11, 3 * 16 + 3, 3 * 16 + 11 # A0:左下角索引，I0:右下角索引，A9:左上角索引，I9:右上角索引

N, E, S, W = -16, 1, 16, -1 # 上，右，下，左
directions = {
    'P': (N, W, E),
    'N': (N+N+E, E+N+E, E+S+E, S+S+E, S+S+W, W+S+W, W+N+W, N+N+W),
    'B': (2 * N + 2 * E, 2 * S + 2 * E, 2 * S + 2 * W, 2 * N + 2 * W),
    'R': (N, E, S, W),
    'C': (N, E, S, W),
    'A': (N+E, S+E, S+W, N+W),
    'K': (N, E, S, W)
}

MATE_LOWER = piece['K'] - (2*piece['R'] + 2*piece['N'] + 2*piece['B'] + 2*piece['A'] + 2*piece['C'] + 5*piece['P']) # 1304
MATE_UPPER = piece['K'] + (2*piece['R'] + 2*piece['N'] + 2*piece['B'] + 2*piece['A'] + 2*piece['C'] + 5*piece['P']) # 3696

TABLE_SIZE = 1e4 # 置换表中最多允许的元素的数量，大概117MB
# TABLE_SIZE = 1e5 # 置换表中最多允许的元素的数量，大概190MB
# # TABLE_SIZE = 1e7 # 置换表中最多允许的元素的数量

QS_LIMIT = 219
EVAL_ROUGHNESS = 2
DRAW_TEST = True
# THINK_TIME = 5 # 思考时间
THINK_TIME = 3 # 思考时间

fakeProgress = 0 # 伪思考进度

###############################################################################
# 象棋逻辑
###############################################################################
class Position(namedtuple('Position', 'board score')):
    """ A state of a chess game
    board -- 占用256字节的棋盘，一维元组
    score -- 棋盘的估值
    """
    def gen_moves(self): # 生成棋子可能走法
        for i, p in enumerate(self.board): # 遍历棋盘上的每个棋子
            if p == 'K': # 该点棋子为将
                for scanpos in range(i-16, A9, -16): # 把将一直往上走
                    if self.board[scanpos] == 'k': # 对老将
                        yield (i,scanpos) # 返回起点和终点位置
                    elif self.board[scanpos] != '.': # 中间有棋子，不能对老将，退出
                        break
            if not p.isupper(): continue # 不是红色棋子，（黑子或无子）不进行搜索
            if p == 'C': # 该点棋子为炮
                for d in directions[p]: # 炮可以往上下左右四个方向走
                    cfoot = 0
                    for j in count(i+d, d): # 迭代器，从i+d开始每次增加d
                        q = self.board[j] # 获取目标点棋子标号
                        if q.isspace():break # 标号为空格，出棋盘了，结束循环，换个方向走
                        if cfoot == 0 and q == '.':yield (i,j) # 没有炮架子，炮可以正常行走
                        elif cfoot == 0 and q != '.':cfoot += 1 # 第一次遇到炮架子
                        elif cfoot == 1 and q.islower(): yield (i,j);break # 有炮架子并且炮架子后面有黑色棋子，可以吃子，将起点和该点坐标返回
                        elif cfoot == 1 and q.isupper(): break # 炮架子后面是自己的棋子，不能走
                continue
            for d in directions[p]: # 遍历p棋子的可能行走方向
                for j in count(i+d, d): # 迭代器，从i+d开始每次增加d
                    q = self.board[j] # 获取目标点棋子标号
                    if q.isspace() or q.isupper(): break # 出棋盘了或者吃自己的子，退出
                    if p == 'P' and d in (E, W) and i > 128: break # 当前棋子是兵，想往左右走，没有过河，退出
                    elif p in ('A','K') and (j < 160 or j & 15 > 8 or j & 15 < 6): break # 当前棋子是士或将，出九宫了，退出
                    elif p == 'B' and j < 128: break # 当前棋子是相，过河了，退出
                    elif p == 'N': # 当前棋子是马
                        n_diff_x = (j - i) & 15 # 负数也可以取余
                        if n_diff_x == 14 or n_diff_x == 2: # 2：左2上1或右2下1，14：左2下1或右2上1
                            if self.board[i + (1 if n_diff_x == 2 else -1)] != '.': break # 蹩马腿
                        else: # 1：左1上2或右1下2，15：左1下2或右1上2
                            if j > i and self.board[i + 16] != '.': break # 蹩马腿
                            elif j < i and self.board[i - 16] != '.': break # 蹩马腿
                    elif p == 'B' and self.board[i + d // 2] != '.':break # 塞象眼
                    yield (i, j) # 以上条件检测都通过了，返回该走法
                    if p in 'PNBAK' or q.islower(): break # 兵，马，象，士，将在一个方向上只能有一种走法，退出

    def rotate(self):
        return Position(
            self.board[-2::-1].swapcase() + " ", -self.score)

    def nullmove(self):
        return self.rotate()

    def move(self, move): # move：用户的走法
        i, j = move # i：起点坐标，j：终点坐标
        p, q = self.board[i], self.board[j] # p:起点棋子id，q：终点棋子id

        board = self.board
        score = self.score + self.value(move)
    
        board = board[:j] + board[i] + board[j+1:] # 将起点棋子放到终点
        board = board[:i] + '.' + board[i+1:] # 将起点设为空子
        return Position(board, score).rotate() # 棋盘旋转，分数取负

    def value(self, move): # 估值函数
        i, j = move
        p, q = self.board[i], self.board[j] # p:起点棋子id，q：终点棋子id
        score = pst[p][j] - pst[p][i] # 分数=终点棋子子力-起点棋子子力
        if q.islower(): # 如果吃子
            score += pst[q.upper()][255-j-1] #　加上被吃的棋子的分数
        return score

###############################################################################
# 搜索逻辑
###############################################################################
Entry = namedtuple('Entry', 'lower upper')

class Searcher:
    def __init__(self):
        self.tp_score = {}
        self.tp_move = {}
        self.history = set()
        self.nodes = 0 # 节点数

    def bound(self, pos, gamma, depth, root=True):
        self.nodes += 1

        depth = max(depth, 0)
        if pos.score <= -MATE_LOWER:
            return -MATE_UPPER

        if DRAW_TEST:
            if not root and pos in self.history:
                return 0

        entry = self.tp_score.get((pos, depth, root), Entry(-MATE_UPPER, MATE_UPPER))
        if entry.lower >= gamma and (not root or self.tp_move.get(pos) is not None):
            return entry.lower
        if entry.upper < gamma:
            return entry.upper

        # move函数↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        def moves():
            if depth > 0 and not root and any(c in pos.board for c in 'RNC'):
                yield None, -self.bound(pos.nullmove(), 1-gamma, depth-3, root=False)

            if depth == 0:
                yield None, pos.score

            killer = self.tp_move.get(pos)
            if killer and (depth > 0 or pos.value(killer) >= QS_LIMIT):
                yield killer, -self.bound(pos.move(killer), 1-gamma, depth-1, root=False)
            for move in sorted(pos.gen_moves(), key=pos.value, reverse=True):
                if depth > 0 or pos.value(move) >= QS_LIMIT:
                    yield move, -self.bound(pos.move(move), 1-gamma, depth-1, root=False)
        # move函数↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

        best = -MATE_UPPER
        for move, score in moves():
            best = max(best, score)
            if best >= gamma:
                if len(self.tp_move) > TABLE_SIZE: self.tp_move.clear()
                self.tp_move[pos] = move
                break

        if best < gamma and best < 0 and depth > 0:
            is_dead = lambda pos: any(pos.value(m) >= MATE_LOWER for m in pos.gen_moves())
            if all(is_dead(pos.move(m)) for m in pos.gen_moves()):
                in_check = is_dead(pos.nullmove())
                best = -MATE_UPPER if in_check else 0

        if len(self.tp_score) > TABLE_SIZE: self.tp_score.clear()
        if best >= gamma:
            self.tp_score[pos, depth, root] = Entry(best, entry.upper)
        if best < gamma:
            self.tp_score[pos, depth, root] = Entry(entry.lower, best)

        return best

    def search(self, pos, history=()): # 搜索算法，参数:(当前棋局，历史棋局)
        self.nodes = 0 # 节点清零
        if DRAW_TEST:
            self.history = set(history) # 去重
            self.tp_score.clear()

        for depth in range(1, 1000):
            lower, upper = -MATE_UPPER, MATE_UPPER # 可能出现的最低分数，可能出现的最高分数
            while lower < upper - EVAL_ROUGHNESS:
                gamma = (lower+upper+1)//2
                score = self.bound(pos, gamma, depth)
                if score >= gamma:
                    lower = score
                if score < gamma:
                    upper = score

                # 串口发送过伪进度↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
                # 假定fakeProgress范围为[0,55]
                global fakeProgress
                fakeProgress += 1
                print('\rfakeProgress:', fakeProgress, end='')
                if fakeProgress > 54:
                    fakeProgress = 54
                SendString('PB,%d' % (int(fakeProgress * 124 / 55))) # 串口发送伪搜索进度
                # 串口发送过伪进度↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

            self.bound(pos, lower, depth)
            yield depth, self.tp_move.get(pos), self.tp_score.get((pos, depth, True),Entry(-MATE_UPPER, MATE_UPPER)).lower

###############################################################################
# 转换
###############################################################################
def parse(c): # 将棋盘坐标转换为一维元组的索引
    return ((ord(c[0])-ord('a')+3)<<4) | (ord(c[1])+3-ord('0'))


def render(i): # 将一维元组的索引转换为棋盘坐标
    return chr((i>>4)-3+ord('a')) + chr((i&15)-3+ord('0'))


def gen_moves_2(board): # 生成棋子可能走法
    for i, p in enumerate(board): # 遍历棋盘上的每个棋子
        if p == 'K': # 该点棋子为将
            for scanpos in range(i-16, A9, -16): # 把将一直往上走
                if board[scanpos] == 'k': # 对老将
                    yield (i,scanpos) # 返回起点和终点位置
                elif board[scanpos] != '.': # 中间有棋子，不能对老将，退出
                    break
        if not p.isupper(): continue # 不是红色棋子，（黑子或无子）不进行搜索
        if p == 'C': # 该点棋子为炮
            for d in directions[p]: # 炮可以往上下左右四个方向走
                cfoot = 0
                for j in count(i+d, d): # 迭代器，从i+d开始每次增加d
                    q = board[j] # 获取目标点棋子标号
                    if q.isspace():break # 标号为空格，出棋盘了，结束循环，换个方向走
                    if cfoot == 0 and q == '.':yield (i,j) # 没有炮架子，炮可以正常行走
                    elif cfoot == 0 and q != '.':cfoot += 1 # 第一次遇到炮架子
                    elif cfoot == 1 and q.islower(): yield (i,j);break # 有炮架子并且炮架子后面有黑色棋子，可以吃子，将起点和该点坐标返回
                    elif cfoot == 1 and q.isupper(): break # 炮架子后面是自己的棋子，不能走
            continue
        for d in directions[p]: # 遍历p棋子的可能行走方向
            for j in count(i+d, d): # 迭代器，从i+d开始每次增加d
                q = board[j] # 获取目标点棋子标号
                if q.isspace() or q.isupper(): break # 出棋盘了或者吃自己的子，退出
                if p == 'P' and d in (E, W) and i > 128: break # 当前棋子是兵，想往左右走，没有过河，退出
                elif p in ('A','K') and (j < 160 or j & 15 > 8 or j & 15 < 6): break # 当前棋子是士或将，出九宫了，退出
                elif p == 'B' and j < 128: break # 当前棋子是相，过河了，退出
                elif p == 'N': # 当前棋子是马
                    n_diff_x = (j - i) & 15 # 负数也可以取余
                    if n_diff_x == 14 or n_diff_x == 2: # 2：左2上1或右2下1，14：左2下1或右2上1
                        if board[i + (1 if n_diff_x == 2 else -1)] != '.': break # 蹩马腿
                    else: # 1：左1上2或右1下2，15：左1下2或右1上2
                        if j > i and board[i + 16] != '.': break # 蹩马腿
                        elif j < i and board[i - 16] != '.': break # 蹩马腿
                elif p == 'B' and board[i + d // 2] != '.':break # 塞象眼
                yield (i, j) # 以上条件检测都通过了，返回该走法
                if p in 'PNBAK' or q.islower(): break # 兵，马，象，士，将在一个方向上只能有一种走法，退出


def IsCheck(board, move): # move为一维坐标
    board2 = copy.deepcopy(board)

    i, j = move # i：起点坐标，j：终点坐标
    p, q = board2[i], board2[j] # p:起点棋子id，q：终点棋子id

    board2 = board2[:j] + board2[i] + board2[j+1:] # 将起点棋子放到终点
    board2 = board2[:i] + '.' + board2[i+1:] # 将起点设为空子

    for i in gen_moves_2(board2):
        if board2[i[1]] == 'k': # 终点是对方的将
            return True
    return False

###############################################################################
# 接口函数
###############################################################################

searcher = Searcher() # 实例化搜索引擎
hist = None # 实例化一个象棋逻辑对象


# 加入一个初始化棋盘的函数
def ElephantFishChessInit(chessBoard):
    global hist
    mappingTable = ['.','k','r','n','c','a','b','p','K','R','N','C','A','B','P',' '] # 两种棋盘棋子的映射表
    # 将二维列表棋盘转为一维字符串棋盘
    chessString = (' '*15+'\n')*3
    for i in chessBoard:
        chessString += '   '
        for j in i:
            chessString += mappingTable[j]
        chessString += '   \n'
    chessString += (' '*15+'\n')*3

    hist = [Position(chessString, 0)] # 传入初始棋局，实例化Position对象，该对象实现走法生成器，估值函数


def ElephantFishChessSE(move): # move格式如:'h7h4'
    move = parse(move[:2]), parse(move[2:])

    if move not in hist[-1].gen_moves():
        return 'invalid' # 玩家走棋非法

    hist.append(hist[-1].move(move)) # 将该走法添加进历史表

    if hist[-1].score <= -MATE_LOWER: # 当前分数小于等于最小值，玩家胜利
        return -1 # 要发送个信息提示

    start = time.time()
    for _depth, move, score in searcher.search(hist[-1], hist):
        if time.time() - start > THINK_TIME: # 超时退出
            break
    end = time.time()

    # 串口发送伪进度↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    global fakeProgress
    for i in range(fakeProgress, 55+1):
        SendString('PB,%d' % (int(i * 124 / 55))) # 串口发送搜索完成的进度
        time.sleep(0.01) # 进度条渐变
    fakeProgress = 0
    print('\nfakeProgress:end')
    # 串口发送伪进度↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    # if score == MATE_UPPER: # 将军检测，这个检测方法有问题
    #     print("Checkmate!")

    # 思考进度怎么弄？弄个伪进度，范围0-55，最多显示到54，再刷新就是直接100%了

    pcCaptureFlag = hist[-1].board[move[1]].islower() # 判断电脑是否吃子，小写字母是对面的棋子，大写字母是自己的棋子
    pcCheckFlag = IsCheck(hist[-1].board, move) # 判断电脑是否将军

    hist.append(hist[-1].move(move))

    if hist[-1].score <= -MATE_LOWER: # 电脑胜利
        return 1

    move = render(255-move[0] - 1) + render(255-move[1]-1) # 将一维坐标转为二维坐标

    return pcCheckFlag, pcCaptureFlag, move, _depth, end-start

