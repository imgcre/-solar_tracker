import utest
from highord import *
import _thread
import syncpri
import pyb
from ucollections import namedtuple
import uinspect
from utilities import *


class TestSyncPri(utest.TestCase):

    @utest.cond(equals(1))
    def test_func1(self):
        mutex = syncpri.SpinMutex()

        @infinite_loop_thread
        def low_freq():
            with mutex:
                pyb.LED(1).off()
                pyb.delay(500)
            pyb.delay(500)

        @infinite_loop_thread
        def high_freq():
            with mutex:
                pyb.LED(1).toggle()
            pyb.delay(50)

    @utest.cond(equals(2))
    def test_multi_spin_mutex(self):
        TProp = namedtuple('TProp', ('mutex', 'led', 'id'))
        props = [TProp(syncpri.SpinMutex(), pyb.LED(led_id), led_id) for led_id in (1, 2, 4)]

        @infinite_loop_thread
        def led_select():
            for prop in props:
                others = [p for p in props if p is not prop]
                [other.mutex.acquire() or other.led.off() for other in others]
                pyb.delay(500)
                [other.mutex.release() for other in others]

        @infinite_loop_thread_for(*props)
        def led_blink(prop):
            with prop.mutex:
                prop.led.toggle()
            pyb.delay(prop.id * 25)

    @utest.cond(equals(3))
    def test_event_thread(self):
        print('call set_event() to set the event')
        event = syncpri.Event()
        setattr(uinspect.main_module, 'set_event', lambda: event.set())

        @infinite_loop_thread
        def led_blink():
            with event, Indicator(1):
                pyb.delay(1000)


if __name__ == '__main__':
    print('tests list:')
    print('1. test for single SpinMutex')
    print('2. test for multi SpinMutexes')
    print('3. test for event using original lock on thread')
    x = int(input('please choose one: '))
    utest.main(x)
