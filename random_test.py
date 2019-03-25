from pyb import *
from main import *


def test1():
    # 舵机测试
    LED(2).on()
    while True:
        for i in range(180):
            Servo(1).angle(i - 90)
            delay(20)
        for i in range(180):
            Servo(1).angle(90 - i)
            delay(20)


def test2():
    adc_x5 = ADC(Pin('X5'))
    adc_x6 = ADC(Pin('X6'))
    adc_x7 = ADC(Pin('X7'))
    adc_x8 = ADC(Pin('X8'))
    # 步进电机测试 X2  X3
    # 舵机测试
    # 四路ADC测试
    i = -90
    dir_ = False
    while True:
        stepper.step()
        Servo(1).angle(i)
        if dir_:
            i -= 1
            if i <= -90:
                dir_ = False
        else:
            i += 1
            if i >= 90:
                dir_ = True
        print([adc_xx.read() for adc_xx in [adc_x5, adc_x6, adc_x7, adc_x8]])
        pyb.delay(100)
    pass


def test3():
    # 读取测试

    pass


if __name__ == '__main__':
    test2()
