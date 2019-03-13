from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys
import csv


# (月, 日, 时, 分, 秒)
class MyTime(tuple):
    # 以秒为单位返回大致时间差
    # 假设一个月是30天
    def __sub__(self, other):
        factors = [2_592_000, 86_400, 3_600, 60, 1]
        sum_ = 0
        for i in range(len(factors)):
            sum_ += (self[i] - other[i]) * factors[i]
        return sum_


class MyConfig:
    conf = csv.CSV('config.csv')

    @classmethod
    def get_region(cls, cur_time: MyTime):
        raw_record = cls.__parse_record(cls.conf.binary_search(
            lambda record: cls.__parse_record(record)['time'] > cur_time))
        print(raw_record)

        # TODO: None 的情况
        if raw_record['time'] < cur_time:
            cls.conf.cur_record()  # 跳过当前记录
            while True:
                if not cls.conf.cur_record(move_to_next=False):
                    print('meet last!')
                    return cls.__parse_record(cls.conf.prev_record()), None
                if cls.__parse_record(cls.conf.cur_record())['time'] > cur_time:
                    cls.conf.prev_record()
                    break
            cls.conf.prev_record()
        elif raw_record['time'] > cur_time:
            while True:
                if cls.conf.get_cur_record_id() == 0:
                    return None, cls.__parse_record(cls.conf.cur_record())
                if cls.__parse_record(cls.conf.prev_record())['time'] <= cur_time:
                    break

        return cls.__parse_record(cls.conf.cur_record()), cls.__parse_record(cls.conf.cur_record())

    @staticmethod
    def __parse_record(record):
        return {
            'time': MyTime([int(item) for item in record[:-2]] + [0]),
            'angle': {
                'pitch': int(record[4]),
                'yaw': float(record[5])
            } if record else None
        }


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
            region = MyConfig.get_region(cur_time)
            print(region)

            pyb.delay(20)
    except Exception:
        with Indicator(1):  # 发生错误, 则闪红灯
            pyb.delay(20)


stop = rtc_tick.dispose
