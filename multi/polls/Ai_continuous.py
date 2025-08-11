import ctypes            #数据C类型化
from ctypes import *
import numpy as np       #调用numpy包 需要下载

Ai = np.zeros(8000,dtype='float32')
dll = windll.LoadLibrary(r'.\lib\x64\USB5000.dll')


##########################################################################################################
DevIndex = ctypes.c_int(0)        #将数据转换c数据类型      索引 一张卡默认是0
ChanselON = ctypes.c_char(1)      #设置1为开通道
ChanselOFF = ctypes.c_char(0)     #设置0位关闭通道
Range = ctypes.c_float(10)        #量程         设置量程 设置为10代表正负10V量程范围，可以设置多种量程详情请参考编程手册
AiSampleMode = ctypes.c_char(0)   #设置采集模式  0为连续采集模式  1为oneshot模式
AiSampleRate = ctypes.c_int(1000000)  #设置采样周期 这里是设置的数据是以ns为单位的采样周期 1000000ns 换算为采样率为1000HZ
AiTrigSource = ctypes.c_char(0)   #设置采集卡触发源 设置0为软件触发   执行SetUSB5AiSoftTrig()函数即可触发采集
                                  #它有多种触发方式 具体触发方式需要详细参考函数手册
AiConvSource = ctypes.c_char(0)   #设置采集卡时钟源  设置0为设置 0 代表 Ai 内部采样时钟源，该时采样时钟频率由SetUSB5AiSampleRate()函数设定。
                                  #多有多种时钟源可设置 具体可参考函数手册
Num = ctypes.c_long(100)          #单次从缓冲区获取的点数  它点数建议设置为单通道采样率的十分之一 或者 五分之一
TimeOut = ctypes.c_long(1000)     #超时时间 在设定的超时时间内需要获取到Num个点数，如果获取不到 将会报错
############################################################################################################

A = dll.USB5OpenDevice(DevIndex)                          #启动采集卡要执行的第一个函数 打开采集卡
for i in range(0,8):
    temp = dll.SetUSB5AiChanSel(DevIndex, i, ChanselOFF)  #采集卡默认开启8通道 先提前关闭8通道  然后再进行通道的开启
for i in range(0,1):
    temp = dll.SetUSB5AiChanSel(DevIndex, i, ChanselON)   #开启 0通道 设置量程
    temp = dll.SetUSB5AiRange(DevIndex,i,Range)
#############################################################################################################
temp = dll.SetUSB5AiSampleMode(DevIndex,AiSampleMode)     #设置采集模式
print(temp)
temp = dll.SetUSB5AiSampleRate(DevIndex,AiSampleRate)     #设置采样周期
print(temp)
temp = dll.SetUSB5AiTrigSource(DevIndex, AiTrigSource)    #设置触发源
print(temp)
temp = dll.SetUSB5AiConvSource(DevIndex, AiConvSource)    #设置采集卡模拟采样时钟源 一般都是使用模拟输入功能自身的采样时钟源
print(temp)
temp = dll.SetUSB5ClrAiFifo(DevIndex)                     #采集FIFO缓冲区大小是2M数据空间  为方式缓冲区有数据 先进行、清除AI缓冲区数据
print(temp)
temp = dll.SetUSB5AiSoftTrig(DevIndex)                    #执行软件触发函数 触发采集卡采集
print(temp)

#这里仅仅执行10次GetAi函数    若需要进行连续采集 则可以连读不断执行getai函数即可

################################################################################################
for i in range(0,10):
    # Getai函数的返回值 代表采集卡缓冲区还有多少数据点  正常情况下返回值是一个大于等0切不随时间增大而增大的数值 如果随时间增大而增大 则代表获取的数据点少或执行效率低
    temp9= dll.USB5GetAi(DevIndex,Num, Ai.ctypes.data_as(POINTER(c_float)), TimeOut)
    # 每通道读取 100个点存放于 Ai矩阵中，这里参数Ai.ctypes.data_as(POINTER(c_float))为指向Ai矩阵的指针，超时时间为 1000ms
    # 数据存放规则为前 100个数据是 Ai 0 通道；
    # 接下来 100个数据是 Ai 1 通道；
    # 接下来 100 个数据是 Ai 2 通道；
    # timeout是以ms为单位 它的设定代表在timeout内 需要从fifo缓冲区获取到100数据点  如没有获取到 则会报超时的错误 -7
    print(temp9)
    print(Ai[0:100])
##################################################################################################
dll.SetUSB5ClrAiTrigger(DevIndex)   #清除Ai触发信号
dll.SetUSB5ClrAiFifo(DevIndex)      #清空AiFifo
dll.USB5CloseDevice(DevIndex)

#函数值返回0即为正确执行次函数  如果返回负数  则需对照编程手册查看错误返回代码 查找问题

#详情参数设置  请参数官网smacq.cn对应产品系列的函数手册进行更多了解