from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys
import csv

# tween
# 编写及测试config
# recentTime

# MyConfig.get_region((1,1,5,0, 0))

# MyConfig.get_region((1,6,12,0, 0))
# MyConfig.get_region((1,6,11,59, 0))

# MyConfig.get_region((1,6,11,39, 0))
# {'time': (1, 6, 11, 20, 0), 'angle': {'yaw': 0.0, 'pitch': -10}}
# ({'time': (1, 6, 11, 40, 0), 'angle': {'yaw': 0.0, 'pitch': -5}}, {'time': (1, 6, 12, 0, 0), 'angle': {'yaw': 0.0, 'pitch': 0}})

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


# 总是会更小一点
class MyConfig:
    conf = csv.CSV('config.csv')

    @classmethod
    def get_region(cls, cur_time: MyTime):
        raw_record = cls.__parse_record(cls.conf.binary_search(lambda record: cls.__parse_record(record)['time'] > cur_time))

        # 这个是左边界, 所以如果 小于 cur_time, 则往右边直到找到大于cur_time的，然后回滚
        # 如果大于cur_time, 则回滚, 直到出现小于cur_time的情况，就停止

        print(raw_record)

        # TODO: None 的情况
        if raw_record['time'] < cur_time:  # FIXME: 右半边为None
            cls.conf.cur_record()  # 跳过当前记录
            while True:
                if not cls.conf.cur_record(move_to_next=False):
                    return cls.__parse_record(cls.conf.cur_record()), None
                if cls.__parse_record(cls.conf.cur_record())['time'] > cur_time:
                    cls.conf.prev_record()
                    break
            cls.conf.prev_record()
        elif raw_record['time'] > cur_time:  # FIXED: 左半边为None
            while True:
                print(cls.conf.get_cur_record_id())
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


config = csv.CSV('config.csv')
test = csv.CSV('config.csv')


def record_to_time(record):
    return MyTime([int(item) for item in record[:-2]] + [0])


# search(1, 3, 17, 0, 1)

def search(*args):
    def gt(items):
        return record_to_time(items) > args
    return config.binary_search(gt)


# 刚好相等的情况的测试
def do():
    while True:
        record = test.cur_record()
        if not record:
            break
        cur_time = record_to_time(record)

        with Indicator():
            test_time = record_to_time(search(*cur_time))
        if test_time != cur_time:
            print('at', cur_time, '->', test_time, 'smaller' if test_time < cur_time else 'bigger')


class Config:
    f = open('config.csv', 'rt')

    @staticmethod
    def parse_item(line):
        if not line:
            return None
        items = line[:-1].split(',')
        return {
            'time': MyTime([int(item) for item in items[:-2]] + [0]),
            'angle': {
                'pitch': int(items[4]),
                'yaw': float(items[5])
            }
        }

    @classmethod
    def get_recent_item_pair(cls, cur_time):
        prev_line = ''
        while True:
            next_line = cls.f.readline()
            print(next_line)
            next_item, prev_item = [cls.parse_item(line) for line in (next_line, prev_line)]
            if prev_line or cls.f.tell() == len(next_line):  # 循环是否第一次执行, 或者在文件首
                if ((not prev_item and next_item['time'] > cur_time)
                        or (not next_item and prev_item['time'] <= cur_time)
                        or (prev_item and next_line and prev_item['time'] <= cur_time < next_item['time'])):
                    cls.f.seek(*(-len(next_line), 1) if next_line else [0])
                    cls.f.seek(-len(prev_line), 1)
                    return prev_item, next_item
            prev_line = next_line

    # 记录是有序的, 则可以二分查找
    @classmethod
    def search_recent_item_pair(cls, cur_time):
        # 如果天数少于1天, 则
        pass


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
