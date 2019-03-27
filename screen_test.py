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


@map_to_thread(partial(ExtInt)(Pin('Y5'), ExtInt.IRQ_FALLING, Pin.PULL_UP))
def key1():
    delay(10)  # 消抖
    print('key1 pressed!')


if __name__ == '__main__':
    utest.main()
