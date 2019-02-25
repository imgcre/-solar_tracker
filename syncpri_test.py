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
        mutex1 = syncpri.SpinMutex()
        mutex2 = syncpri.SpinMutex()

        def low_freq():
            while True:
                with mutex1:
                    pyb.LED(1).off()
                    pyb.delay(500)
                with mutex2:
                    pyb.LED(2).off()
                    pyb.delay(500)

        def led1_blink():
            while True:
                with mutex1:
                    pyb.LED(1).toggle()
                pyb.delay(50)

        def led2_blink():
            while True:
                with mutex2:
                    pyb.LED(2).toggle()
                pyb.delay(50)
            pass

        _thread.start_new_thread(low_freq, [])
        _thread.start_new_thread(led1_blink, [])
        _thread.start_new_thread(led2_blink, [])


if __name__ == '__main__':
    print('tests list:')
    print('1. test for one SpinMutex')
    print('2. test for two SpinMutexes')
    x = int(input('please choose: '))
    utest.main(x)
