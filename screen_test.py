import utest
from highord import *
from display import *
from pyb import *
from screen import *
from utilities import *
from cmemgr import Mapper

oled = OLED(I2C(2, mode=I2C.MASTER))
console = Console(oled)
oled.init()

# 四个按钮: 上 左 右 确定


class TestConsole(utest.TestCase):
    def test_random_points(self):
        oled.clear()
        console[1][1] = 'Current Time:'
        console[2][3] = '/'
        console[2][9] = ':'
        with console.padding(2, char='0'):
            console[2][1] = 3
            console[2][4] = 31
            console[2][7] = 23
            console[2][10] = 0


# [2][1] 是两位整数
cur_num = 0


def padding(num, min_len=2):
    s = str(num)
    return '0' * (2 - len(s)) + s


# 这个按键应该是物理上坏了
@key_handler('Y5')
def key1():
    print('key1 pressed!')
    # global cur_num
    # cur_num -= 1
    # print(cur_num)
    # console[2][1] = str(cur_num)

# 只允许往上调整时间
# 月 日 时 分


@key_handler('Y6')
def key2():
    global cur_num
    cur_num -= 1
    with console.padding(2, char='0'):
        console[2][1] = cur_num


@key_handler('Y7')
def key3():
    global cur_num
    cur_num += 1
    with console.padding(2, char='0'):
        console[2][1] = cur_num


@key_handler('Y8')
def key4():
    print('key4 pressed!')


if __name__ == '__main__':
    utest.main()
    Mapper.run(use_main_thread=True)
