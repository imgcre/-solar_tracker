import utest
from highord import *
from utilities import *


class TestUtilities(utest.TestCase):
    @utest.cond(equals(1))
    def test_soft_timer(self):
        obj = ObjLike()
        obj.val = [0, 0, 0]

        def increase(idx):
            obj.val[idx] += 1

        for i in range(3):
            SoftTimer.default_register(partial(increase)(i), (11, 63, 233)[i])

        def printer():
            print(obj.val)

        SoftTimer.default_register(printer, 1)

    @utest.cond(equals(2))
    def test_tween(self):
        tween = Tween(init_val=0, target_val=255, expected_duration=20)
        tween.on_updated = pyb.LED(4).intensity
        tween.on_completed = lambda: tween.set_target(255 if tween.cur_value == 0 else 0)


if __name__ == '__main__':
    print('tests list:')
    print('1. test for soft timer')
    print('2. test for tween')
    x = int(input('please choose one: '))
    utest.main(x)
