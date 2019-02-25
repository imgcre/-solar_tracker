import utest
from highord import *
import syncpri


class TestSyncPri(utest.TestCase):

    @utest.cond(equals(1))
    def test_func1(self):
        print('cond=1 satisfied')


    def test_func2(self):
        print('cond=2 satisfied')


if __name__ == '__main__':
    print('tests list:')
    print('1. LED blink for ')
    utest.main(1)
