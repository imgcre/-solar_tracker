from pyb import *
from cmemgr import map_to_thread
from utilities import *
import sys
import csv

# 步距角=1.8° -> 200

# p = Pin('X1')  # X1 has TIM2, CH1
# tim = Timer(2, freq=6400)
# ch = tim.channel(1, Timer.PWM, pin=p)
# ch.pulse_width_percent(50)




class Stepper:
    def __init__(self, step_name, dir_name):
        self.step_pin = Pin(step_name, Pin.OUT_PP)
        self.dir_pin = Pin(dir_name, Pin.OUT_PP)

    # 如果time是负数, 则反向旋转
    def step(self, times=None, *, period=10, direction=0):
        if times:
            print('dir =', times)
            for _ in range(abs(int(times))):
                self.step(direction=times > 0, period=period)
        else:

            self.dir_pin.value(direction)
            self.step_pin.on()
            delay(int(period / 2))
            self.step_pin.off()
            delay(int(period / 2))


stepper = Stepper('X2', 'X3')

stepper_tween = Tween(unit=1.8,  # 电机步长 -> 1.8°
                      update_with_diff=True,
                      on_updated=stepper.step)

stepper_tween.set_target(20, expected_duration=1000)

def rev():
    if stepper_tween.cur_value == 20:
        stepper_tween.set_target(0)
    else:
        stepper_tween.set_target(20)
    pass


stepper_tween.on_completed = rev

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
                'pitch': int(record[5]),
                'yaw': float(record[4])
            } if record else None
        }


ds3231 = I2C(1, I2C.MASTER)
prev_region = []

servo_tween = Tween(max_speed=0.01,
                    refresh_rate=1,
                    auto_tick=False,
                    on_updated=Servo(1).angle)

stepper_tween = Tween(unit=1.8 / 32,  # 电机步长 -> 1.8°
                      max_speed=9 / 1000,
                      refresh_rate=1,
                      auto_tick=False,
                      update_with_diff=True,
                      on_updated=stepper.step)


@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_tick():
    global prev_region, servo_tween, stepper_tween
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

                time_diff_ms = 1000 * (region[1]['time'] - region[0]['time'])
                servo_tween.set_target(region[1]['angle']['pitch'], expected_duration=time_diff_ms)
                stepper_tween.set_target(region[1]['angle']['yaw'], expected_duration=time_diff_ms)
            stepper_tween.tick()
            servo_tween.tick()
    except Exception as e:
        with Indicator(1):  # 发生错误, 则闪红灯
            print(e)
            pyb.delay(20)


stop = rtc_tick.dispose
