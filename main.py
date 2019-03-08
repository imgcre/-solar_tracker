from pyb import *
from cmemgr import map_to_thread
from utilities import partial


@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_second():
    LED(1).toggle()


