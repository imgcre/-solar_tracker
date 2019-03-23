from pyb import *
from main import *

stepper = Stepper('X2', 'X3')


def test1():
    LED(2).on()
    while True:
        stepper.step()
        delay(5)


def test2():

    pass


if __name__ == '__main__':
    test1()
