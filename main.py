from pyb import *
from cmemgr import map_to_thread
from utilities import partial


ds3231 = I2C(1, I2C.MASTER)

@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_second():
    # [秒, 分, 时, 星期, 日, 月, 年]
    time_info = [b & 0x0f + (b & 0xf0) * 10 for b in ds3231.mem_read(7, 104, 0)]
    print(time_info)


