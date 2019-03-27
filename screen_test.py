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
        pass


if __name__ == '__main__':
    utest.main()
