import utest
from highord import *
from display import *
from pyb import *
import uos

oled = OLED(I2C(2, mode=I2C.MASTER))
oled.init()


class TestOLED(utest.TestCase):
    @utest.cond(equals(1))
    def test_random_points(self):
        oled.clear()
        while True:
            #with oled.session:
            for i in range(64):
                oled[i][63-i] = 0
            for i in range(64):
                oled[i][i] = 1
            #with oled.session:
            for i in range(64):
                oled[i][i] = 0
            for i in range(64):
                oled[i][63-i] = 1


if __name__ == '__main__':
    print('tests list:')
    print('1. test for random points')
    x = int(input('please choose one: '))
    utest.main(x)
