# coding=utf-8

import copy

import Global as glo
from SerialPort import SendString
from ElephantFish import ElephantFishChessSE
from ElephantFish import ElephantFishChessInit


# 棋盘格子尺寸
MM_PER_GRID_X = 30 # 棋盘每格子的宽度，mm
MM_PER_GRID_Y = 30 # 棋盘每格子的高度，mm

# 棋子编号定义
NOCHESS = 0 # 没有棋子

B_KING = 1 # 黑将
B_CAR = 2 # 黑車
B_HORSE = 3 # 黑馬
B_CANNON = 4 # 黑炮
B_BISHOP = 5 # 黑士
B_ELEPHANT = 6 # 黑象
B_PAWN = 7 # 黑卒
B_BEGIN = B_KING
B_END = B_PAWN

R_KING = 8 # 红帅
R_CAR = 9 # 红車
R_HORSE = 10 # 红馬
R_CANNON = 11 # 红炮
R_BISHOP = 12 # 红仕
R_ELEPHANT = 13 # 红相
R_PAWN = 14 # 红兵
R_BEGIN = R_KING
R_END = R_PAWN

UNKNOW = 15 # 未知棋子

chessTextChi = ('+-','将','車','馬','炮','士','象','卒','帅','車','馬','炮','仕','相','兵') # 棋子文本元组

'''
红棋合法位置可以把黑棋合法位置颠倒一下
'''

blackChessValidPos = (
    ((False, False, False,  True,  True,  True, False, False, False ), # 黑将合法位置
    (False, False, False,  True,  True,  True, False, False, False ),
    (False, False, False,  True,  True,  True, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False )),

    (( True,  True,  True,  True,  True,  True,  True,  True,  True ), # 黑車合法位置
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),),
    
    (( True,  True,  True,  True,  True,  True,  True,  True,  True ), # 黑马合法位置
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),),

    (( True,  True,  True,  True,  True,  True,  True,  True,  True ), # 黑炮合法位置
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),),

    ((False, False, False,  True, False,  True, False, False, False ), # 黑士合法位置
    (False, False, False, False,  True, False, False, False, False ),
    (False, False, False,  True, False,  True, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False )),

    ((False, False,  True, False, False, False,  True, False, False ), # 黑象合法位置
    (False, False, False, False, False, False, False, False, False ),
    ( True, False, False, False,  True, False, False, False,  True ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False,  True, False, False, False,  True, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False )),

    ((False, False, False, False, False, False, False, False, False ), # 黑卒合法位置
    (False, False, False, False, False, False, False, False, False ),
    (False, False, False, False, False, False, False, False, False ),
    ( True, False,  True, False,  True, False,  True, False,  True ),
    ( True, False,  True, False,  True, False,  True, False,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True ),
    ( True,  True,  True,  True,  True,  True,  True,  True,  True )))

INIT_CHESSBOARD = ( # 棋局初始状态元组
    (   B_CAR,  B_HORSE, B_ELEPHANT, B_BISHOP,  B_KING, B_BISHOP, B_ELEPHANT,  B_HORSE,   B_CAR ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    ( NOCHESS, B_CANNON,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS, B_CANNON, NOCHESS ),
    (  B_PAWN,  NOCHESS,     B_PAWN,  NOCHESS,  B_PAWN,  NOCHESS,     B_PAWN,  NOCHESS,  B_PAWN ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    (  R_PAWN,  NOCHESS,     R_PAWN,  NOCHESS,  R_PAWN,  NOCHESS,     R_PAWN,  NOCHESS,  R_PAWN ),
    ( NOCHESS, R_CANNON,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS, R_CANNON, NOCHESS ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    (   R_CAR,  R_HORSE, R_ELEPHANT, R_BISHOP,  R_KING, R_BISHOP, R_ELEPHANT,  R_HORSE,   R_CAR ))

# INIT_CHESSBOARD = ( # 棋局初始状态元组
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS,  B_KING, NOCHESS, NOCHESS,  NOCHESS,   NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, B_CANNON,  NOCHESS,    NOCHESS, NOCHESS, NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS,  NOCHESS,  B_CANNON,     NOCHESS,  NOCHESS,  NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
#     (  R_PAWN,  NOCHESS,     R_PAWN,  NOCHESS,  NOCHESS,  NOCHESS,     R_PAWN,  NOCHESS,  R_PAWN ),
#     ( NOCHESS, R_CANNON,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS, R_CANNON, NOCHESS ),
#     ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
#     (   R_CAR,  R_HORSE, R_ELEPHANT, R_BISHOP,  R_KING, R_BISHOP, R_ELEPHANT,  R_HORSE,   R_CAR ))


def IsRed(chessID): # 判断棋子是不是红色棋子
    if R_BEGIN <= chessID <= R_END:
        return True
    return False


def IsBlack(chessID): # 判断棋子是不是黑色棋子
    if B_BEGIN <= chessID <= B_END:
        return True
    return False


def GetOneChessString(chessID): # 获取一个棋子的字符串表达形式
    if IsBlack(chessID):
        return '\033[0;37;40m' + chessTextChi[chessID] + '\033[0m' # 黑色棋子背景显示为黑色
    elif IsRed(chessID):
        return '\033[0;37;41m' + chessTextChi[chessID] + '\033[0m' # 红色棋子背景显示为红色
    return chessTextChi[chessID] # 没有棋子，显示一个'+'


def GetLineChessString(line, n): # 获取一行棋子的字符串表达形式
    chessString = chr(n + ord('A'))+ '    ' # 棋盘左边界
    for i in range(8): # 处理一行的前8个棋子
        chessString += GetOneChessString(line[i]) + '---'
    if line[8] == NOCHESS:
        print(chessString + '+    ' + chr(n + ord('A')))
    else:
        print(chessString + GetOneChessString(line[8]) + '   ' + chr(n + ord('A')))


def PrintChessBoard(chessBoard): # 打印整个棋局
    for i in range(23):
        if i>=2 and i<= 20 and (i-2)%2==0:
            GetLineChessString(chessBoard[int((i-2)/2)], int((i-2)/2))
        elif i==7 or i==9 or i==13 or i==15:
            print('|    |    |    |    |    |    |    |    |    |    |') # 棋盘竖线
        elif i==0 or i==22:
            print('+----0----1----2----3----4----5----6----7----8----+') # 棋盘上下边界
        elif i==1 or i==21:
            print('|                                                 |') # 棋盘边缘
        elif i==3 or i==17:
            print(r'|    |    |    |    |  \ | /  |    |    |    |    |') # 九宫竖线，原样输出，不转义
        elif i==5 or i==19:
            print(r'|    |    |    |    |  / | \  |    |    |    |    |') # 九宫竖线，原样输出，不转义
        elif i==11:
            print('|    |        楚河               汉界        |    |') # 楚河汉界


def MakeMove(chessBoard, movePath): # 根据某一走法产生走之后的棋盘，参数:(当前棋盘,走棋路线)
    # 注意chessBoard为列表，函数内部是更改列表的单个元素值，这样对形参的更改会影响到实参，正好能实现功能
    chessBoard[ord(movePath[2])-ord('a')][ord(movePath[3])-ord('0')] = chessBoard[ord(movePath[0])-ord('a')][ord(movePath[1])-ord('0')] # 将起点的棋子挪到终点
    chessBoard[ord(movePath[0])-ord('a')][ord(movePath[1])-ord('0')] = NOCHESS # 将起点设为无棋子


def PY_ChessInterface(userMovePath): # 参数：(走棋路线)，当前界面为全局变量chessBoardStatus
    chessBoard = copy.deepcopy(glo.getValue('globalChessBoard'))

    MakeMove(chessBoard, userMovePath) # 尝试按照玩家的走棋路线走棋
    PrintChessBoard(chessBoard) # 打印玩家走棋后的棋盘

    print('电脑正在思考...')
    result = ElephantFishChessSE(userMovePath)# 调用ElephantFish程序

    if result == 'invalid': # 玩家走棋违法
        PrintChessBoard(glo.getValue('globalChessBoard'))
        print('玩家走棋非法，请重新输入:')
        return

    if result == 1:
        print('电脑胜利')
        return

    if result == -1:
        print('玩家胜利')
        return

    pcCheckFlag, pcCaptureFlag, pcMovePath, searchDepth, elapsedTime = result # 将军标志位，吃子标志位，电脑走棋路线，搜索深度，耗时
    
    MakeMove(chessBoard, pcMovePath) # 按照电脑走法走棋
    PrintChessBoard(chessBoard) # 打印电脑走棋后的棋盘
    
    print('电脑走棋路线:(%c,%c)->(%c,%c)' % (pcMovePath[0], pcMovePath[1], pcMovePath[2], pcMovePath[3]))
    print('搜索深度:%d,耗时%.3f秒' % (searchDepth, elapsedTime))

    status = 'c1' if pcCaptureFlag & pcCheckFlag else('c2' if pcCheckFlag else('c3' if pcCaptureFlag else 'c4')) # c1：吃子将军，c2：不吃子将军，c3：吃子不将军，c4：不吃子不将军

    # 这儿要改，机械臂精度有问题
    yFrom = (ord(pcMovePath[0])-ord('a')) * MM_PER_GRID_Y + 58 # 起点y坐标
    xFrom = (4-(ord(pcMovePath[1])-ord('0'))) * MM_PER_GRID_X + 3 # 起点x坐标
    yTo = (ord(pcMovePath[2])-ord('a')) * MM_PER_GRID_Y + 58 # 终点y坐标
    xTo = (4-(ord(pcMovePath[3])-ord('0'))) * MM_PER_GRID_X + 3 # 终点x坐标

    OutputPCMovePath = '%s,%d,%d,%d,%d' % (status, int(yFrom), int(xFrom), int(yTo), int(xTo))
    SendString(OutputPCMovePath) # 串口发送电脑走棋路线
    print(OutputPCMovePath)

    glo.setValue('globalChessBoard', chessBoard)


def PY_ChessInit(initChessBoard): # 象棋程序初始化
    glo.setValue('globalChessBoard', list(list(x) for x in initChessBoard)) # 创建一个与initChessBoard有相同参数的列表
    ElephantFishChessInit(initChessBoard) # 棋盘，历史表初始化
    print('\n\n\n')
    PrintChessBoard(glo.getValue('globalChessBoard')) # 打印开局棋盘
    print('棋盘及历史表初始化完成!')

