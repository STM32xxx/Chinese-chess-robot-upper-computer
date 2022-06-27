# coding=utf-8

import serial
import time

import Global as glo


portNumber = serial.Serial() # 先定义一个Serial类的对象


def OpenSerialPort(comx, baudRate, timeout): # 打开串口，参数(端口号，波特率，超时时间)
    global portNumber
    if isinstance(portNumber, serial.Serial): # 判断变量类型是否正确
        portNumber = serial.Serial(comx, baudRate, timeout = timeout)
        if portNumber.isOpen():
            print('串口打开成功!')
        else:
            print('串口打开失败!')
    else:
        print('错误')


def XOR_Get(s): # 得到异或结果
    return '_' # 暂时不使用异或校验
    # res = 0
    # for i in s:
    #     res ^= ord(i) # 异或校验
    # return res


def XOR_Check(s, XOR_Res): # 异或校验
    res = 0
    for i in s:
        res ^= ord(i)
    return res == XOR_Res


'''
按照上下位机之间的协议发送数据
一帧数据格式如：#10,RC,177,105*_;
'#'为起始字节，10为数据长度，即(RC,177,105)的长度，后跟命令类型：RC：机械臂坐标，PB：进度条，cx：走棋命令，UK：未知棋子列表，
'*'为分隔符，'_'为数据异或校验，即(RC,177,105)的异或校验，';'为结束字节
形参data只是数据，不包括起始字节，数据长度，'*'分隔符，校验值，结束字节
'''
def SendString(data):
    portNumber.write(('#%d,%s*%c;' % (len(data), data, XOR_Get(data))).encode('utf-8')) # 串口发送一帧数据


def SerialPortThread():
    while True:
        data = portNumber.read_all() # 读取串口接收缓冲区
        if data == b'': # 缓冲区无数据
            # 发送搜索进度
                # 调用GetPos()获取搜索进度
                # 通过串口发送给下位机
            pass
        else: # 缓冲区接受到数据
            if data == b'c': # 接收到字符'c'，表示玩家已落子
                print('玩家已落子，开始检测...')
                # 调用opencv，等待opencv检测完成，改一下，直接调用函数，不用再创建线程，但这样只有执行到这儿的时候摄像头画面才能刷新
                glo.setValue('statisticsRun', True)
                while glo.getValue('statisticsRun'):
                    pass # 等待OpenCV统计完成
            elif data == b'f': # 接收到字符'f'，表示是残局对弈，需要先识别棋盘状态
                print('残局对弈，识别棋盘状态...')
                glo.setValue('endGameFlag', True)
                while glo.getValue('endGameFlag'):
                    pass # 等待残局统计完成
            elif data == b'j': # 接收到字符'j'，表示是机器摆棋，需要先识别棋盘状态
                print('机器摆棋，识别棋盘状态...')
                glo.setValue('newGameFlag', True)
                while glo.getValue('newGameFlag'):
                    pass # 等待棋盘状态统计完成
            elif data == b'r': # 接收到字符'r'，表示校正机械臂，摄像头判断到机械臂时发送坐标
                print('校正机械臂...')
                glo.setValue('robotCorrect', True)
            elif data == b'o': # 接收到字符'o'，表示机械臂校正完成
                print('机械臂校正完成!')
                glo.setValue('robotCorrect', False)
            else:
                print('接受到其他命令:', data)

        time.sleep(0.1) # 100ms



