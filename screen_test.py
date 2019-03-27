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


# [2][1] 是两位整数
cur_num = 0


@key_handler('Y5')
def key1():
    global cur_num
    cur_num -= 1
    print(cur_num)
    console[1][1] = "%02d" % (cur_num,)


@key_handler('Y6')
def key2():
    global cur_num
    cur_num += 1
    print(cur_num)
    console[1][1] = "%02d" % (cur_num,)


@key_handler('Y7')
def key3():
    print('key3 pressed!')


@key_handler('Y8')
def key4():
    print('key4 pressed!')


if __name__ == '__main__':
    utest.main()
