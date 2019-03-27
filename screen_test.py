import utest
from highord import *
from display import *
from pyb import *
from screen import *

oled = OLED(I2C(2, mode=I2C.MASTER))
console = Console(oled)
oled.init()


class TestConsole(utest.TestCase):
    def test_random_points(self):
        oled.clear()
        console[0][0] = 'Current Time:'
        console[1][0] = '03/27 19:00'


if __name__ == '__main__':
    utest.main()
