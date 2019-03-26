import utest
from highord import *
from display import *
from pyb import *
import uos

oled = OLED(I2C(2, mode=I2C.MASTER))


class TestOLED(utest.TestCase):
    @utest.cond(equals(1))
    def test_random_points(self):
        oled.init()
        while True:
            x = uos.urandom(1)[0] % 128
            y = uos.urandom(1)[0] % 64
            color = uos.urandom(1)[0] % 2
            oled.draw_point(x, y, color)
        pass

    pass


if __name__ == '__main__':
    print('tests list:')
    print('1. test for random points')
    x = int(input('please choose one: '))
    utest.main(x)
