# coding=utf-8

import threading, re

import Global as glo

from ChessInterface import PY_ChessInit
from ChessInterface import PY_ChessInterface
from ChessInterface import INIT_CHESSBOARD # 常规开局初始棋盘

from SerialPort import OpenSerialPort
from SerialPort import SerialPortThread
from OpenCV import OpenCVThread


'''
Jetson Nano上先运行 'sudo chmod 777 /dev/ttyTHS1' 指令打开串口
'''
runtimeEnvironment = 'windows' # 运行环境，windows或linux


def Main():
    glo._init() # 全局变量初始化
    glo.setValue('statisticsRun', False) # opencv运行标志位，在SerialPort和OpenCV中使用
    glo.setValue('endGameFlag', False) # 残局标志位，在SerialPort和OpenCV中使用
    glo.setValue('newGameFlag', False) # 机器摆棋标志位，在SerialPort和OpenCV中使用
    glo.setValue('robotCorrect', False) # 机械臂校正标志位，在SerialPort和OpenCV中使用
    glo.setValue('globalChessBoard', [[0]*9 for i in range(10)]) # 全局棋盘，在OpenCV和Chess中使用

    # 以下参数为默认参数，如果配置文件读取失败，将使用默认参数
    glo.setValue('serialPortNumber', '/dev/ttyTHS1' if runtimeEnvironment=='linux' else 'COM5') # 默认串口号
    glo.setValue('cameraNumber', 1) # 默认摄像头编号
    glo.setValue('houghCirclesDeteThreshold', 600) # 默认霍夫圆检测阈值，在OpenCV中使用
    glo.setValue('robotDeteThreshold', 200) # 默认机械臂检测阈值，在OpenCV中使用
    glo.setValue('colorClassifyThreshold', 110) # 默认红黑棋子分类阈值，在OpenCV中使用

    ReadConfigFile('config.txt') # 读取配置文件

    # 打开串口
    OpenSerialPort(glo.getValue('serialPortNumber'), 115200, 0.02)

    # 创建串口监听线程
    serialPortThread = threading.Thread(target=SerialPortThread) # 创建串口监听线程
    # 加入判断线程是否创建成功代码
    serialPortThread.setDaemon(True) # 设置为守护线程，主线程结束后自动结束
    serialPortThread.start() # 线程开始运行

    # 创建OpenCV线程
    opencvThread = threading.Thread(target=OpenCVThread) # 创建OpenCV线程
    # # 加入判断线程是否创建成功代码
    opencvThread.setDaemon(True) # 设置为守护线程，主线程结束后自动结束
    opencvThread.start() # 线程开始运行
    # OpenCV线程退出有问题，要先关闭摄像头

    PY_ChessInit(INIT_CHESSBOARD) # 象棋初始化

    while True:
        cmd = input() # 等待输入命令

        cmd = cmd.lower() # 命令全部转换成小写
        if cmd == 'new game': # 新游戏
            print('new game is ok')
        elif cmd == 'undo': # 悔棋
            print('undo is ok')
        elif cmd == 'redo': # 还原
            print('redo is ok')
        elif cmd == 'stop': # 停止思考
            print('stop is ok')
        elif cmd == 'exit': # 退出
            return
        elif cmd == '?':
            PrintHelpMessage() # 打印帮助信息
        else:
            searchDepth = re.findall(r'(?<=set search depth )\d|(?<=ssd )\d', cmd) # 提取设置的搜索深度
            if searchDepth:
                searchDepth = ord(searchDepth[0]) - ord('0')
                print(searchDepth) # 切换搜索深度
                continue

            movePath = re.findall(r'^[0-8]?[a-j][0-8]?[0-8]?[a-j][0-8]?$', cmd) # 提取走棋路线命令
            if movePath and len(movePath[0]) == 4:
                movePath = movePath[0] # 只要第一个匹配结果
                movePathTemp = '' # 空字符串

                movePathTemp += (movePath[0] + movePath[1]) if movePath[0].isalpha() else (movePath[1] + movePath[0])
                movePathTemp += (movePath[2] + movePath[3]) if movePath[2].isalpha() else (movePath[3] + movePath[2])

                chessThread = threading.Thread(target=PY_ChessInterface, args=(movePathTemp,))
                chessThread.setDaemon(True)
                chessThread.start()
                continue

            print('命令错误,输入?查看帮助.')


def ReadConfigFile(file): # 打开配置文件，读取上次设置
    try:
        with open(file, 'r', encoding='utf-8') as f:
            title  = f.readline() # 配置文件标题
            try: # 尝试读取配置文件，覆盖默认参数
                comMessage = f.readline() # 包含串口信息，在后面使用正则表达式匹配
                if runtimeEnvironment == 'windows': # 在windows上运行，从配置文件读取串口号，在linux上运行默认为'/dev/ttyTHS1'
                    serialString = re.findall(r'(?<=serialPortNumber=)\w+', comMessage)[0]
                    glo.setValue('serialPortNumber', serialString)
                cameraNumber = int(re.findall(r'(?<=cameraNumber=)\d+', f.readline())[0])
                glo.setValue('cameraNumber', cameraNumber)
                houghCirclesDeteThreshold = int(re.findall(r'(?<=houghCirclesDeteThreshold=)\d+', f.readline())[0])
                glo.setValue('houghCirclesDeteThreshold', houghCirclesDeteThreshold)
                robotDeteThreshold = int(re.findall(r'(?<=robotDeteThreshold=)\d+', f.readline())[0])
                glo.setValue('robotDeteThreshold', robotDeteThreshold)
                colorClassifyThreshold = int(re.findall(r'(?<=colorClassifyThreshold=)\d+', f.readline())[0])
                glo.setValue('colorClassifyThreshold', colorClassifyThreshold)
                # print(serialString, cameraNumber, houghCirclesDeteThreshold, robotDeteThreshold, colorClassifyThreshold)
            except IndexError:
                print('配置文件参数错误，错误参数将按照默认参数进行设置...')
    except FileNotFoundError: # 抛出文件不存在异常
        print('未找到配置文件，按照默认参数进行设置...')


def WriteConfigFile(file): # 写入配置文件
    with open(file, 'w', encoding='utf-8') as f:
        f.write('# 象棋机器人配置文件\n')
        f.write('serialPortNumber=%s 		# 串口号\n' % glo.getValue('serialPortNumber'))
        f.write('cameraNumber=%d 			# 摄像头编号\n' % glo.getValue('cameraNumber'))
        f.write('houghCirclesDeteThreshold=%d 	# 霍夫圆检测阈值\n' % glo.getValue('houghCirclesDeteThreshold'))
        f.write('robotDeteThreshold=%d 		# 机械臂检测阈值\n' % glo.getValue('robotDeteThreshold'))
        f.write('colorClassifyThreshold=%d 		# 红黑棋子分类阈值\n' % glo.getValue('colorClassifyThreshold'))
    print('配置文件写入完成!')


def PrintHelpMessage(): # 打印输出帮助信息
    print('Updating...')
    # print('************************************帮助信息********************************************')
    # print('0.所有指令不区分大小写')
    # print('1.输入\'set search depth x\'或\'ssd x\'设置搜索深度,x为搜索深度,取值范围0-8')
    # print('2.输入\'set hough ciecles threshold x\'或\'shct x\'设置霍夫圆检测阈值')
    # print('3.输入\'set robot arm threshold x\'或\'srat x\'设置机械臂检测阈值')
    # print('4.输入\'set chess classify threshold x\'或\'shct x\'设置霍夫圆检测阈值')
    # print('5.输入\'set hough ciecles threshold x\'或\'scct x\'设置红黑棋子分类阈值')
    # print('6.走棋命令类似于h7h4')
    # print('**********************************以上是帮助信息****************************************')


if __name__ == '__main__':
    try:
        Main()
    except KeyboardInterrupt:
        print('按键中断，退出游戏')

    print('后续处理,待加入...')
    # 结束创建的进程
    # 销毁OpenCV窗口

    WriteConfigFile('config.txt') # 保存配置文件



