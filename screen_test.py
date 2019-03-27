import utest
from highord import *
from display import *
from pyb import *
from screen import *

oled = OLED(I2C(2, mode=I2C.MASTER))
console = Console(oled)
oled.init()

# 四个按钮: 上 左 右 确定

class TestConsole(utest.TestCase):
    def test_random_points(self):
        oled.clear()
        console[1][1] = 'Current Time:'



if __name__ == '__main__':
    utest.main()
