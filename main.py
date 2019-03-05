import pyb
import cmemgr
import syncpri
import _thread
from dsl import *
from uinspect import *
import highord

class Test:
    def __get__(self, instance, owner):
        return 5
        pass
    pass