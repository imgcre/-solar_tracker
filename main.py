from pyb import *
from cmemgr import map_to_thread
from screen import *
from utilities import *
import sys
from cmemgr import Mapper
from context import ContextChain
import csv
import ustruct

# 步距角=1.8° -> 20

# X1 -> 舵机  -> P13
# X2、X3 -> 步进 -> P14、P15
# X5 X6 X7 X8 -> ADC
# X9 X10 X11 (SCL SDA SWQ) RTC

# Y5 Y6 Y7 Y8 按钮
#


class Stepper:
    def __init__(self, step_name, dir_name):
        self.step_pin = Pin(step_name, Pin.OUT_PP)
        self.dir_pin = Pin(dir_name, Pin.OUT_PP)

    # 如果time是负数, 则反向旋转
    def step(self, times=None, *, period=10, direction=0):
        if times:
            for _ in range(abs(int(times))):
                self.step(direction=times > 0, period=period)
        else:
            self.dir_pin.value(direction)
            self.step_pin.on()
            delay(int(period / 2))
            self.step_pin.off()
            delay(int(period / 2))


stepper = Stepper('X2', 'X3')
adc_list = [ADC(Pin(pin_name)) for pin_name in ['X5', 'X6', 'X7', 'X8']]


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
                'pitch': float(record[5]),
                'yaw': int(record[4])
            } if record else None
        }


# TODO: 改回用软件定时器的owo
inited = False
fast_move_mode = False

prev_region = []
servo_tween = Tween(max_speed=0.01,
                    refresh_rate=1,
                    auto_tick=False,
                    on_updated=Servo(1).angle)
stepper_tween = Tween(unit=1.8,  # 电机步长 -> 1.8°
                      max_speed=9 / 1000,
                      refresh_rate=1,
                      auto_tick=False,
                      update_with_diff=True,
                      on_updated=stepper.step)


ds3231 = I2C(1, I2C.MASTER)
cur_sel = -1
cur_time_disp = [1, 1, 0, 0, 0]


@map_to_thread(partial(ExtInt)(Pin('X11'), ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE))
def rtc_tick():
    global prev_region, servo_tween, stepper_tween, inited, cur_time_disp, fast_move_mode
    try:
        with Indicator():
            if cur_sel < 0:
                time_info = [(b & 0x0f) + (b >> 4) * 10 for b in ds3231.mem_read(7, 104, 0)]
                cur_time = MyTime((time_info[5], time_info[4], time_info[2], time_info[1], time_info[0]))
                cur_time_disp = list(cur_time)
                redraw()
                # 无条件阈值设置为1000
                # cancel 条件: 都大于某个值, 且两两之间的差值不超过存在超过某个值
                adc_vals = [adc.read() for adc in adc_list]
                if all([adc_val > 1000 for adc_val in adc_vals] + [
                        abs(adc_inner - adc_outer) < 100 for adc_inner in adc_vals for adc_outer in adc_vals]):
                    print('canceled')
                    servo_tween.cancel()
                    stepper_tween.cancel()

                # print(cur_time)
                region = MyConfig.get_region(cur_time)
                if region != prev_region or fast_move_mode:
                    time_diff_ms = 3000
                    # 准备加载新的目标值
                    if not fast_move_mode:
                        print('region changed to', region)
                        prev_region = region
                        time_diff_ms = 1000 * (region[1]['time'] - region[0]['time'])

                    target_pitch = region[1]['angle']['pitch']
                    target_yaw = region[1]['angle']['yaw']
                    src_pitch = region[0]['angle']['pitch']
                    src_yaw = region[0]['angle']['yaw']

                    # 快速到达目标位置
                    if not inited:
                        inited = True

                    if fast_move_mode:
                        # (当前时间 - 起始时间) / (目标时间 - 起始时间)
                        rate = (cur_time - region[0]['time']) / (region[1]['time'] - region[0]['time'])
                        target_pitch = src_pitch + (target_pitch - src_pitch) * rate
                        target_yaw = src_yaw + (target_yaw - src_yaw) * rate
                        fast_move_mode = False
                        # TODO: add target
                        pass

                    # TODO: 快速从设置前时间的值变到当前时间的值
                    servo_tween.set_target(target_pitch, expected_duration=time_diff_ms)
                    stepper_tween.set_target(target_yaw, expected_duration=time_diff_ms)
                stepper_tween.tick()
                servo_tween.tick()
    except Exception as e:
        with Indicator(1):  # 发生错误, 则闪红灯
            print(e)
            pyb.delay(20)

    globals()['stop'] = rtc_tick.dispose


oled = OLED(I2C(2, mode=I2C.MASTER))
console = Console(oled)
oled.init()
oled.clear()

val_borders = [(1, 12), (1, 30), 23, 59, 59]
separator = ['/', ' ', ':', ':']


def redraw():
    with console.session:
        console[1][1] = 'Time:'
        for i in range(len(separator)):
            console[2][(i + 1) * 3] = separator[i]
        for i in range(len(cur_time_disp)):
            cc = ContextChain([console.padding(2, char='0')])
            if cur_sel == i:
                cc.append(console.reverse)
            with cc:
                console[2][1 + 3 * i] = cur_time_disp[i]
        console[4][1] = 'Pitch:'
        console[5][1] = 'Yaw:'
        with console.padding(4):
            console[4][8] = str(servo_tween.cur_value)[:4]
            console[5][8] = str(servo_tween.cur_value)[:4]


# 调整当前时间
@key_handler('Y6')
def key2():
    if cur_sel >= 0:
        cur_time_disp[cur_sel] += 1
        cur_border = val_borders[cur_sel]
        min_val, max_val = cur_border if type(cur_border) is tuple else (0, cur_border)
        cur_time_disp[cur_sel] = (cur_time_disp[cur_sel] - min_val) % (max_val - min_val + 1) + min_val
        redraw()


# 进入时间设置模式/选择当前时间
@key_handler('Y7')
def key3():
    global cur_sel
    cur_sel += 1
    cur_sel %= len(cur_time_disp)
    redraw()


# 确认更改
@key_handler('Y8')
def key4():
    # 确认
    global cur_sel, fast_move_mode
    ds3231.mem_write(ustruct.pack('bbbbbbb', *[b // 10 * 16 + b % 10 for b in [
        cur_time_disp[4], cur_time_disp[3], cur_time_disp[2], 0, cur_time_disp[1], cur_time_disp[0], 0]]), 104, 0)
    cur_sel = -1
    fast_move_mode = True
    redraw()
    # 向iic写入当前时间
    # 记得先转成bcd


redraw()
Mapper.run(use_main_thread=True)
