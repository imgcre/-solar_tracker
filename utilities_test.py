import utest
from utilities import Tween
from highord import *
from utilities import *


class TestUtilities(utest.TestCase):
    @utest.cond(equals(1))
    def test_soft_timer(self):
        obj = ObjLike()
        obj.val = [0, 0, 0]

        def increase(idx):
            obj.val[idx] += 1

        for i in [10, 50, 100]:
            SoftTimer.default_register(partial(increase)(i), 50)

        def printer():
            print(obj.val)

        SoftTimer.default_register(printer, 1)

    @utest.cond(equals(2))
    def test_tween(self):
        # 呼吸灯
        pass
    pass


if __name__ == '__main__':
    print('tests list:')
    print('1. test for single thread')
    print('2. test for tween')
    x = int(input('please choose one: '))
    utest.main(x)
