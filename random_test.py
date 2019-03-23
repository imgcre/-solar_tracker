from pyb import *
from main import *


def test1():
    LED(2).on()
    while True:
        for i in range(180):
            Servo(1).angle(i - 90)
            delay(20)
        for i in range(180):
            Servo(1).angle(90 - i)
            delay(20)



def test2():

    pass


if __name__ == '__main__':
    test1()
