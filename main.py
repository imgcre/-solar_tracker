from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys

# tween
# 编写及测试config
# recentTime


f = open('config.csv', 'rb')

sys.exit()

global_vars = ObjLike()
ds3231 = I2C(1, I2C.MASTER)

@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_tick():
    # [秒, 分, 时, 星期, 日, 月, 年]
    # 只需要关心: 月 日 时 分
    # 求得对应的: 水平角度 俯仰角度
    try:
        with Indicator():
            time_info = [(b & 0x0f) + (b >> 4) * 10 for b in ds3231.mem_read(7, 104, 0)]
            print(time_info)

            if global_vars.get('inited') is None:
                global_vars.inited = True
                # 初始化相关代码

            pyb.delay(20)
    except Exception:
        with Indicator(1):  # 发生错误, 则闪红灯
            pyb.delay(20)


stop = rtc_tick.dispose
