import utest
from highord import *
import _thread
import syncpri
import pyb
from ucollections import namedtuple


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
    def test_multi_spin_mutex(self):
        TProp = namedtuple('TProp', ('mutex', 'led', 'id'))
        props = [TProp(syncpri.SpinMutex(), pyb.LED(led_id), led_id) for led_id in (1, 2, 4)]

        def led_select():
            while True:
                for prop in props:
                    others = [p for p in props if p is not prop]
                    [other.mutex.acquire() or other.led.off() for other in others]
                    pyb.delay(500)
                    [other.mutex.release() for other in others]

        def led_blink(prop):
            while True:
                with prop.mutex:
                    prop.led.toggle()
                pyb.delay(prop.id * 25)

        _thread.start_new_thread(led_select, [])
        [_thread.start_new_thread(led_blink, [prop]) for prop in props]


if __name__ == '__main__':
    print('tests list:')
    print('1. test for single SpinMutex')
    print('2. test for multi SpinMutexes')
    x = int(input('please choose: '))
    utest.main(x)
