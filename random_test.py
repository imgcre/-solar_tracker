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
    # 步进电机测试 X2  X3
    stepper = Stepper('X3', 'X4')
    while True:
        stepper.step()
        pyb.delay(100)
    pass


if __name__ == '__main__':
    test2()
