from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys

# tween
# 编写及测试config
# recentTime

# (月, 日, 时, 分, 秒)
class MyTime(tuple):
    pass


class Config:
    f = open('config.csv', 'rt')

    @staticmethod
    def get_item(line):
        if not line:
            return None
        items = line[:-1].split(',')
        obj = {
            'time': MyTime([int(item) for item in items[:-2]] + [0]),
            'angle': {
                'pitch': int(items[4]),
                'yaw': float(items[5])
            }
        }
        return obj

    @classmethod
    def get_recent_item_pair(cls, cur_time):
        # TODO: 到达文件尾的情况, 和文件首部的情况
        prev_line = None
        while True:
            next_line = cls.f.readline()
            next_item = cls.get_item(next_line)
            if prev_line or cls.f.tell() == len(next_line):  # 循环是否第一次执行, 或者在文件首
                prev_item = cls.get_item(prev_line)
                if (not prev_item and next_item['time'] > cur_time
                    ) or (not next_item and prev_item['time'] <= cur_time
                          ) or (prev_item and next_line and ['time'] <= cur_time < next_item['time']):
                    cls.f.seek(*(-len(next_line), 1) if not next_line else [0])
                    return prev_item, next_item
            prev_line = next_line


sys.exit()


ds3231 = I2C(1, I2C.MASTER)


@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_tick():
    # [秒, 分, 时, 星期, 日, 月, 年]
    # 只需要关心: 月 日 时 分 秒
    # 求得对应的: 水平角度 俯仰角度
    try:
        with Indicator():
            time_info = [(b & 0x0f) + (b >> 4) * 10 for b in ds3231.mem_read(7, 104, 0)]
            print(time_info)

            # 返回一个包含两个时间的元组
            cur_time = MyTime((time_info[5], MyTime[4], MyTime[2], MyTime[1], MyTime[0]))
            pair = Config.get_recent_item_pair(cur_time)

            pyb.delay(20)
    except Exception:
        with Indicator(1):  # 发生错误, 则闪红灯
            pyb.delay(20)


stop = rtc_tick.dispose
