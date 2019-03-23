from pyb import *

ch = None
def test1():
    global ch
    LED(1).on()
    # 步进电机测试
    p = Pin('X2')  # X1 has TIM2, CH1
    tim = Timer(2, freq=400)
    ch = tim.channel(2, Timer.PWM, pin=p)
    ch.pulse_width_percent(50)


def test2():

    pass


if __name__ == '__main__':
    test1()
