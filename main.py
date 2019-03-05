import pyb
import cmemgr
import syncpri
import _thread
from dsl import *
from uinspect import *
import highord
import utilities

class Descr(object):
    def __get__(self, instance, owner):
        print('been got')
        return 0

class Test(object):
    d = Descr()
    def __init__(self):
        self.d = type(self).d


x = Test()
