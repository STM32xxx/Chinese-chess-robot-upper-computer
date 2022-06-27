# coding=utf-8

import cv2, time, copy, threading
import numpy as np

import Global as glo
import ChessInterface as ch
from SerialPort import SendString
from SerialPort import XOR_Get


recognizerRed = cv2.face.LBPHFaceRecognizer_create()
recognizerRed.read('CascadeClassifierModel/RedChess_AdjustLevels.yml') # 导入红色棋子yml文件，是经过色阶调整后的
recognizerBlack = cv2.face.LBPHFaceRecognizer_create()
recognizerBlack.read('CascadeClassifierModel/BlackChess.yml') # 导入黑色棋子yml文件

chessBoardEdgeBefore = (178, 50, 523, 432) # 棋盘格子外轮廓,(左上角x坐标,左上角y坐标,右下角x坐标,右下角y坐标),→为x正方向，↓为y正方向
windowEdge = (chessBoardEdgeBefore[0]-35, chessBoardEdgeBefore[1]-35, chessBoardEdgeBefore[2]+35, chessBoardEdgeBefore[3]+35) # 感兴趣区域，窗口边缘
chessBoardEdgeAfter = (35, 35, chessBoardEdgeBefore[2]-chessBoardEdgeBefore[0]+35, chessBoardEdgeBefore[3]-chessBoardEdgeBefore[1]+35) # (35, 35, 380, 417),(43.125, 42.444)
gridSize = (int((chessBoardEdgeAfter[2]-chessBoardEdgeAfter[0])/8+0.6), int((chessBoardEdgeAfter[3]-chessBoardEdgeAfter[1])/9+0.6)) # 棋盘一格所占的像素大小，计算下来为43

chessTextAscii = ('No','King','Car','Hor','Cann','Bis','Elep','Pawn','King','Car','Hor','Cann','Bis','Elep','Pawn','Uk') # 用于标记的文本

# 滑动条回调函数↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
def HoughCirclesCallbackFun(self): # 霍夫圆检测阈值滑动条回调函数
    glo.setValue('houghCirclesDeteThreshold', cv2.getTrackbarPos('HoughCircles', 'ChessBoard') + 1) # 该值必须大于0

def RobotDeteCallbackFun(self): # 机械臂检测阈值滑动条回调函数
    glo.setValue('robotDeteThreshold', cv2.getTrackbarPos('RobotDetection', 'ChessBoard'))

def ColorClassifyCallbackFun(self): # 红黑棋子分类阈值滑动条回调函数
    glo.setValue('colorClassifyThreshold', cv2.getTrackbarPos('Color Classify', 'ChessBoard'))
# 滑动条回调函数↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


def OpenCVThread():
    # camera = cv2.VideoCapture(glo.getValue('cameraNumber'), cv2.CAP_DSHOW) # 打开usb摄像头
    camera = cv2.VideoCapture(glo.getValue('cameraNumber')) # windows上会有警告，加上cv2.CAP_DSHOW参数就没警告了
    # camera = cv2.VideoCapture(1, cv2.CAP_DSHOW) # 打开usb摄像头

    cv2.namedWindow('ChessBoard', cv2.WINDOW_AUTOSIZE) # 建立显示窗口，大小不可调

    cv2.createTrackbar('HoughCircles', 'ChessBoard', glo.getValue('houghCirclesDeteThreshold'), 1500, HoughCirclesCallbackFun) # 创建霍夫圆检测阈值滑动条
    cv2.createTrackbar('RobotDetection', 'ChessBoard', glo.getValue('robotDeteThreshold'), 400, RobotDeteCallbackFun) # 创建机械臂检测阈值滑动条
    cv2.createTrackbar('Color Classify', 'ChessBoard', glo.getValue('colorClassifyThreshold'), 255, ColorClassifyCallbackFun) # 创建红黑棋子分类阈值滑动条

    imgChess30_30Kernel = np.array([[False if i+j<9 or i+j>49 or i>j+20 or j>i+20 else True for j in range(30)]for i in range(30)])
    statEndGameChessBoard = [[0]*9 for i in range(10)] # 统计残局棋盘变量，对endGameChessBoard中的数据进行统计得到结果
    userChessBoardLast = [[0]*9 for i in range(10)]
    endGameCount = 0
    unknownChessList = [] # 未知棋子列表，残局统计中用来保存未识别出种类的棋子，随着识别过程进行该列表的元素会越来越少，为空时全部识别完成
    statEndGamsStageFlag = False # 残局统计区分两阶段的标志位

    while True:
        start = time.time() # 记录开始时间
        ok, imgSource = camera.read() # 读取一帧图片
        if not ok: # 未读取到图片，退出
            print('未读取到图片!')
            break

        # 预处理
        imgSource = imgSource[windowEdge[1]:windowEdge[3], windowEdge[0]:windowEdge[2]] # 裁剪掉多余区域，保留感兴趣区域
        imgGray = cv2.cvtColor(imgSource, cv2.COLOR_BGR2GRAY) # RGB转灰度图
        imgHSV = cv2.cvtColor(imgSource, cv2.COLOR_BGR2HSV) # RGB转HSV，使用HSV通道判断棋子颜色
        imgMedian = cv2.medianBlur(imgGray, 3) # 中值滤波
        # imgGaussianBlur = cv2.GaussianBlur(imgGray, (3,3), 0) # 高斯模糊，可以试一下效果，相对于中值滤波速度能快
        imgEqualizeHist = cv2.equalizeHist(imgMedian) # 直方图均衡化

        # 变量清零
        userChessBoard = [[0]*9 for i in range(10)] # 将用户棋盘清空，准备接收摄像头采集的棋盘信息
        userChessNumCount = pcChessNumCount = 0 # 摄像头扫描的玩家棋子数量，摄像头扫描的电脑棋子数量
        grayMin_1 = grayMin_2 = 300000 # 单个棋子所有像素灰度值最小值和次小值
        grayMinXY = [0, 0]

        # 输入图像，方法（类型），dp(dp=1时表示霍夫空间与输入图像空间的大小一致，dp=2时霍夫空间是输入图像空间的一半，以此类推)，最短距离-可以分辨是两个圆否 则认为是同心圆 ,边缘检测时使用Canny算子的高阈值，越低对圆的要求越低，中心点累加器阈值—候选圆心（霍夫空间内累加和大于该阈值的点就对应于圆心），检测到圆的最小半径，检测到圆的的最大半径
        circles = cv2.HoughCircles(imgEqualizeHist, cv2.HOUGH_GRADIENT, 1, 32, param1=glo.getValue('houghCirclesDeteThreshold'), param2=20, minRadius=10, maxRadius=22)
        if circles is not None: # 检测到了棋子
            for circle in circles[0]: # 遍历所有识别到的棋子
                x, y, r = int(circle[0]), int(circle[1]), 16 # 提取圆心坐标，半径固定为16

                if x<chessBoardEdgeAfter[0]-16 or x>chessBoardEdgeAfter[2]+16 or y<chessBoardEdgeAfter[1]-16 or y>chessBoardEdgeAfter[3]+16:
                    continue # 如果棋子过于靠近边缘，后面提取的局域图像将会超出范围，忽略这个棋子

                imgChess30_30 = np.array(imgEqualizeHist[y-15:y+15, x-15:x+15]) * imgChess30_30Kernel # 截取单个象棋图片，30*30像素大小，将9倒角像素值清零
                
                if glo.getValue('robotCorrect'): # 校正机械臂时执行该程序
                    # 统计机械臂，机械臂检测流程：找到灰度值最低和次低的两个圆，如果最低值比次低值还要低上一部分，认为灰度最低值的圆是机械臂标记
                    # 统计机械臂，当接收到机械臂较正命令时，
                    grayPixelValueCount = np.sum(imgChess30_30) # 统计所有像素值的和，用于判断机械臂
                    if grayPixelValueCount < grayMin_2:
                        grayMin_2 = grayPixelValueCount
                        if grayMin_2 < grayMin_1:
                            grayMin_1, grayMin_2 = grayMin_2, grayMin_1
                            grayMinXY = [x, y]
                    continue # 校正机械臂时就不识别棋子了

                imgChess30_30 = imgChess30_30 < 80 # 像素值小于80，为黑色，此时imgChess30_30为0-1矩阵
                blackPixelCount = np.sum(imgChess30_30) + 1 # 统计黑色像素点数，该值必须大于0，防止后面除零异常
                whitePixelCount = 720 - blackPixelCount # 统计白色像素点数，未使用到
                imgChess30_30 = imgChess30_30 * np.array(cv2.split(imgSource[y-15:y+15, x-15:x+15])[2]) # 将imgSource中R通道非红色区域清零
                redPixelValueCount  = np.sum(imgChess30_30) # 统计imgSource中R通道的像素值和

                chessBoardX, chessBoardY = int((x-17)/43), int((y-17)/43) # 像素坐标转换为棋盘坐标，43就是gridSize
                if redPixelValueCount / blackPixelCount > glo.getValue('colorClassifyThreshold'): # 红色，blkPixNum+1是为了防止blkPixNum=0导致除零异常
                    cv2.circle(imgSource, (x,y), 4, (0,255,0), -1) # 红色棋子用绿点标记
                    userChessBoard[chessBoardY][chessBoardX] = ch.R_BEGIN # 8
                    userChessNumCount += 1
                else: # 黑色
                    cv2.circle(imgSource, (x,y), 4, (255,255,255), -1) # 黑色棋子用白点标记
                    userChessBoard[chessBoardY][chessBoardX] = ch.B_BEGIN # 1
                    pcChessNumCount += 1



                # # 测试
                # rec = imgGray[y-11:y+11, x-11:x+11]
                # imgID, conf = recognizerRed.predict(rec) if ch.IsRed(userChessBoard[chessBoardY][chessBoardX]) else recognizerBlack.predict(rec)
                # cv2.putText(imgSource, chessTextAscii[imgID] if conf<190 else 'Uk', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)




                if [chessBoardY, chessBoardX] in unknownChessList: # 判断当前棋子是否在未识别列表里
                    rec = imgGray[y-11:y+11, x-11:x+11]
                    imgID, conf = recognizerRed.predict(rec) if ch.IsRed(userChessBoard[chessBoardY][chessBoardX]) else recognizerBlack.predict(rec)
                    '''
                    这儿条件如何设置？机器摆棋中任何棋子可以出现在任何位置，无法使用blackChessValidPos这一变量进行限制
                    '''
                    # if conf < 190: # 去掉合法点这一限制条件，试一下这样精度怎么样，才有继续做下去的前提条件
                    #     statEndGameChessBoard[chessBoardY][chessBoardX] = imgID # 将该棋子写入到'统计残局棋盘变量'里
                    #     unknownChessList.remove([chessBoardY,chessBoardX]) # 将该棋子从未知列表删除
                    if conf < 190: # 置信度高于一定值
                        if (ch.IsBlack(imgID) and ch.blackChessValidPos[imgID-1][chessBoardY][chessBoardX]) or (ch.IsRed(imgID) and ch.blackChessValidPos[imgID-8][9-chessBoardY][chessBoardX]): # 如果是黑棋并且该棋子位置合法 或者 是红棋并且该棋子位置合法
                            statEndGameChessBoard[chessBoardY][chessBoardX] = imgID # 将该棋子写入到'统计残局棋盘变量'里
                            unknownChessList.remove([chessBoardY,chessBoardX]) # 将该棋子从未知列表删除

        # 判断是否是机械臂，向下位机发送坐标↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        if glo.getValue('robotCorrect'): # 校正机械臂时执行该程序
            if grayMin_2 * 100 / grayMin_1 > glo.getValue('robotDeteThreshold') and grayMin_2 != 300000: # 放大100倍，适应滑动条
                cv2.circle(imgSource, tuple(grayMinXY), 16, (255,0,0), 2)
                robotX = 120 - (grayMinXY[0] - 35) / 1.4375
                robotY = (grayMinXY[1] - 35) / 1.4148 + 55 # 将摄像头坐标转为棋盘坐标
                SendString('RC,%d,%d' % (robotX, robotY)) # 串口发送机械臂坐标
        # 判断是否是机械臂，向下位机发送坐标↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

        # 开始统计整个棋局，判断玩家走棋路线，仅限常规开局和残局对弈一步之后↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        if glo.getValue('statisticsRun'):
        # if False:
            chessBoard = glo.getValue('globalChessBoard')

            globalChessNumCount = [ch.IsRed(j) for i in chessBoard for j in i].count(True) # 统计红棋的数量
            chessBoardMatch = [ch.IsRed(chessBoard[i][j]) ^ ch.IsRed(userChessBoard[i][j]) for j in range(9) for i in range(10)] # 判断是否只有一个棋子位置发生改变

            if userChessNumCount==globalChessNumCount and chessBoardMatch.count(True)==2: # 判断摄像头扫描到的玩家棋子数量与globalChessBoard中玩家棋子数量是否一致，位置是否只有一个棋子发生改变
                # print('棋子数量无误，并且只有一个棋子移动')
                userMovePath = [0]*4
                breakCount = 0
                for i in range(10):
                    for j in range(9):
                        if ch.IsRed(userChessBoard[i][j]) and not ch.IsRed(chessBoard[i][j]): # 玩家走棋终点
                            userMovePath[2] = i + ord('a')
                            userMovePath[3] = j + ord('0')
                            breakCount += 1
                        elif userChessBoard[i][j]==ch.NOCHESS and ch.IsRed(chessBoard[i][j]): # 玩家走棋起点
                            userMovePath[0] = i + ord('a')
                            userMovePath[1] = j + ord('0')
                            breakCount += 1
                        if breakCount == 2:
                            break
                    if breakCount == 2:
                        break
                print('玩家走棋路线:(%c,%c)->(%c,%c)' % (userMovePath[0], userMovePath[1], userMovePath[2], userMovePath[3]))
                userMovePath = chr(userMovePath[0]) + chr(userMovePath[1]) + chr(userMovePath[2]) + chr(userMovePath[3])

                # 采用调用函数的方式执行象棋程序，此时opencv会暂停运行
                glo.setValue('globalChessBoard', chessBoard)
                ch.PY_ChessInterface(userMovePath) # 象棋接口程序，现在不是单独的线程，执行时OpenCV会停止
                glo.setValue('statisticsRun', False)

                # # 采用创建线程的方式执行象棋程序
                # glo.setValue('globalChessBoard', chessBoard)
                # chessThread = threading.Thread(target=ch.PY_ChessInterface, args=(userMovePath,)) # 创建象棋搜索线程
                # chessThread.setDaemon(True)
                # chessThread.start()
                # glo.setValue('statisticsRun', False) # 统计结束
            else:
                '''
                # 这儿可以加个判断，当多少帧判断都不符合条件，认为是玩家误触按键
                '''
                pass
        # 统计棋局程序结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

        # 统计整个棋局，判断当前棋局状态，仅用于残局对弈第一步↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        if glo.getValue('endGameFlag'):
            if not statEndGamsStageFlag: # 第一阶段，判断出当前棋局的所有棋子位置，棋子颜色
                chessBoardMatch = [(userChessBoardLast[i][j] == userChessBoard[i][j]) for j in range(9) for i in range(10)] # 判断相邻两个棋局是否相等
                endGameCount = endGameCount+1 if chessBoardMatch.count(False) == 0 else 0 # 不等棋子计数为0
                if endGameCount >= 3: # 连续3帧棋盘棋子数量、位置、颜色未发生变化，认为该状态为一个正确的状态
                    unknownChessList = [[i,j] for j in range(9) for i in range(10) if userChessBoard[i][j] != ch.NOCHESS] # 该处有棋子，将棋子坐标添加进未识别列表,下次循环时识别
                    statEndGameChessBoard = [[0]*9 for i in range(10)]# 清空统计棋盘
                    print('第一阶段完成')
                    endGameCount = 0
                    statEndGamsStageFlag = True
            else: # 第二阶段，等待棋子种类识别完成
                if unknownChessList == []: # 未识别棋子列表为空，表示所有棋子都已识别出
                    if not eachChessDetection(statEndGameChessBoard): # 判断每种棋子数量是否正确
                        ch.PrintChessBoard(statEndGameChessBoard)
                        print('棋子数量有误，重新统计!')
                    else:
                        ch.PY_ChessInit(statEndGameChessBoard) # 使用统计后的棋盘初始化象棋程序
                        glo.setValue('endGameFlag', False) # 残局统计完成
                    statEndGamsStageFlag = False
                else:
                    print('unknownChessList',unknownChessList) # 打印未知棋子列表

        userChessBoardLast = copy.deepcopy(userChessBoard)
        # 统计棋局程序结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

        '''
        将识别到的棋子摄像头坐标保存到列表中，
        '''
        # 统计整个棋局，判断当前棋局状态，用于机器摆棋↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        if glo.getValue('newGameFlag'):

            pass
        # 机器摆棋统计结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

        key = cv2.waitKey(5) # 等待5ms按键，这个可以改短
        end = time.time() # 记录结束时间

        cv2.putText(imgSource, 'FPS:%.2f'%(1 / (end-start)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1) # 计算并显示帧率
        cv2.rectangle(imgSource, chessBoardEdgeAfter[:2], chessBoardEdgeAfter[2:], (255,0,255), 1, 4) # 标记棋盘方格最外圈轮廓
        cv2.imshow('ChessBoard', imgSource)

        if key & 0xFF == ord('q'): # 按下'q'退出
            break
            
    camera.release()
    cv2.destroyAllWindows()


def eachChessDetection(chessBoard): # 检测棋盘中每种棋子数量是否正确，即将/帅最多有1个，兵/卒最多有5个，其他最多有2个
    flatChessBoard = list(np.array(chessBoard).flatten()) # 将chessBoard展为一维列表
    if flatChessBoard.count(ch.R_KING)>1 or flatChessBoard.count(ch.B_KING)>1:
        return False
    elif flatChessBoard.count(ch.R_CAR)>2 or flatChessBoard.count(ch.B_CAR)>2:
        return False
    elif flatChessBoard.count(ch.R_HORSE)>2 or flatChessBoard.count(ch.B_HORSE)>2:
        return False
    elif flatChessBoard.count(ch.R_CANNON)>2 or flatChessBoard.count(ch.B_CANNON)>2:
        return False
    elif flatChessBoard.count(ch.R_BISHOP)>2 or flatChessBoard.count(ch.B_BISHOP)>2:
        return False
    elif flatChessBoard.count(ch.R_ELEPHANT)>2 or flatChessBoard.count(ch.B_ELEPHANT)>2:
        return False
    elif flatChessBoard.count(ch.R_PAWN)>5 or flatChessBoard.count(ch.B_PAWN)>5:
        return False
    return True


# OpenCVThread()
# print(gridSize)


'''
棋子编号：
 0--无棋子

 1--黑将
 2--黑車
 3--黑馬
 4--黑象
 5--黑士
 6--黑炮
 7--黑卒

 8--红帅
 9--红車
10--红马
11--红相
12--红士
13--红炮
14--红兵

15--未知
'''


