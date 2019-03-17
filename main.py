from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys
import csv

# 步距角=1.8° -> 200

p = Pin('X1') # X1 has TIM2, CH1
tim = Timer(2, freq=2000)
ch = tim.channel(1, Timer.PWM, pin=p)
ch.pulse_width_percent(50)

sys.exit()


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

        # TODO: None 的情况
        if raw_record['time'] < cur_time:
            cls.conf.cur_record()  # 跳过当前记录
            while True:
                if not cls.conf.cur_record(move_to_next=False):
                    return [cls.__parse_record(cls.conf.prev_record()), None]
                if cls.__parse_record(cls.conf.cur_record())['time'] > cur_time:
                    cls.conf.prev_record()
                    break
            cls.conf.prev_record()
        elif raw_record['time'] > cur_time:
            while True:
                if cls.conf.get_cur_record_id() == 0:
                    return [None, cls.__parse_record(cls.conf.cur_record())]
                if cls.__parse_record(cls.conf.prev_record())['time'] <= cur_time:
                    break

        return [cls.__parse_record(cls.conf.cur_record()), cls.__parse_record(cls.conf.cur_record())]

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
prev_region = []
servo_tween = None
stepper_tween = None

s1 = Servo(1)  # 接X1


@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_tick():
    global prev_region, servo_tween, stepper_tween
    # [秒, 分, 时, 星期, 日, 月, 年]
    # 只需要关心: 月 日 时 分 秒
    # 求得对应的: 水平角度 俯仰角度
    try:
        with Indicator():
            time_info = [(b & 0x0f) + (b >> 4) * 10 for b in ds3231.mem_read(7, 104, 0)]
            cur_time = MyTime((time_info[5], time_info[4], time_info[2], time_info[1], time_info[0]))
            # print(cur_time)
            region = MyConfig.get_region(cur_time)
            if region != prev_region:
                # 准备加载新的目标值
                print('region changed to', region)
                prev_region = region

                if not servo_tween:
                    servo_tween = Tween(init_val=0,
                                        target_val=region[1]['angle']['pitch'],
                                        allow_float=True,
                                        expected_duration=1000*(region[1]['time']-region[0]['time']),
                                        max_speed=0.01,
                                        refresh_rate=1,
                                        auto_tick=False)
                    servo_tween.on_updated = s1.angle
                else:
                    servo_tween.set_target(region[1]['angle']['pitch'],
                                           expected_duration=1000*(region[1]['time']-region[0]['time']))
                if not stepper_tween:
                    # TODO
                    pass
            servo_tween.tick()
    except Exception as e:
        with Indicator(1):  # 发生错误, 则闪红灯
            print(e)
            pyb.delay(20)


stop = rtc_tick.dispose
