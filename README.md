# Chinese-chess-robot-upper-computer
中国象棋机器人上位机

演示视频：https://www.bilibili.com/video/BV1v64y1r7EL?share_source=copy_web

该项目为中国象棋机器人第二版上位机，使用Python重写，可选择在windows或Jetson Nano上运行

#### 所需环境：

- opencv-python==4.5.4.58
- opencv-contrib-python==4.5.4.58
- numpy==1.19.5
- serial==0.0.97
- pyserial==3.5


config.txt文件记录配置信息，包括上位机与下位机通信的串口号、使用的摄像头以及图像处理阈值；

CascadeClassifierModel文件夹下的RedChess.yml与BlackChess.yml文件为级联分类器模型，用于对棋子分类，该模型的训练方法见：xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

环境配置无误，串口地址及摄像头地址无误，输入"pip3 HMI.py"即可运行；



#### 各文件功能：

##### HMI.py:

1. 加载配置文件，进行各种初始化
2. 创建串口通信线程，OpenCV图像处理线程
3. 读取用户指令，进行交互

##### Global.py:

1. 维护所有全局变量，提供统一访问接口

##### OpenCV.py:

1. 对摄像头画面进行ROI区域裁剪、各种滤波等预处理
2. 霍夫圆检测，判断所有棋子的坐标，判断玩家走棋路线
3. 使用级联分类器判断棋子类别（用于残局对弈）
4. 判断机械臂位置，用于开局校正机械臂

##### SerialPort.py:

1. 将待发送的数据进行封装并发送给下位机，接收下位机的数据

##### ElephantFish.py:

1. 一个简单的象棋搜索引擎，输入当前棋局以及玩家走棋路线便可计算一步最优应对策略，可通过限制搜索时间改变其棋力

##### ChessInterface.py:

1. 用于在命令行窗口绘制中国象棋棋局，将象棋对弈过程可视化
