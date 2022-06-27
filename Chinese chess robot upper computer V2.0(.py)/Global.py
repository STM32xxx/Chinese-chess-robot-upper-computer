# coding=utf-8

# 全局变量管理

def _init():
    global _globalDict
    _globalDict = {}


def setValue(key,value):
    _globalDict[key] = value


def getValue(key,defValue=None):
    try:
        return _globalDict[key]
    except KeyError:
        print('字典参数错误')

