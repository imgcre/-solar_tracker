import utest
from highord import *
import _thread
import syncpri
import pyb


class TestSyncPri(utest.TestCase):

    @utest.cond(equals(1))
    def test_func1(self):
        mutex = syncpri.SpinMutex()

        def low_freq():
            while True:
                with mutex:
                    pyb.LED(1).off()
                    pyb.delay(500)
                pyb.delay(500)

        def high_freq():
            while True:
                with mutex:
                    pyb.LED(1).toggle()
                pyb.delay(50)

        _thread.start_new_thread(low_freq, [])
        _thread.start_new_thread(high_freq, [])

    @utest.cond(equals(2))
    def test_func2(self):
        pass


if __name__ == '__main__':
    print('tests list:')
    print('1. test a SpinMutex')
    print('2. test two SpinMutexes')
    x = int(input('please choose: '))
    utest.main(x)
