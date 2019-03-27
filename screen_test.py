import utest
from highord import *
from display import *
from pyb import *
from screen import *
from utilities import *

oled = OLED(I2C(2, mode=I2C.MASTER))
console = Console(oled)
oled.init()

# 四个按钮: 上 左 右 确定


class TestConsole(utest.TestCase):
    def test_random_points(self):
        oled.clear()
        console[1][1] = 'Current Time:'


@key_handler('Y5')
def key1():
    print('key1 pressed!')


@key_handler('Y6')
def key2():
    print('key2 pressed!')


#@key_handler('Y7')
#def key3():
#    print('key3 pressed!')


#@key_handler('Y8')
#def key4():
#    print('key4 pressed!')


if __name__ == '__main__':
    utest.main()
