from pyb import Pin, ExtInt, LED
from cmemgr import map_to_thread

@map_to_thread(lambda cb: ExtInt(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE, cb))
def rtc_second():
    LED(1).toggle()


