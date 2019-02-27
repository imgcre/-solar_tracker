import utest
from highord import *
from uinspect import main_module
import _thread
import cmemgr
import pyb
from utilities import Indicator
from ucollections import namedtuple


class TestCMEMgr(utest.TestCase):
    @utest.cond(equals(1))
    def test_mapper_single_thread(self):
        def caller(func):
            setattr(main_module, 'invoke', func)

        def my_func():
            print('func being called!')

        cmemgr.Mapper(caller, my_func)
        print('type invoke() to call my_func')

    @utest.cond(equals(2))
    def test_mapper_single_interrupt(self):
        tim = pyb.Timer(1)
        tim.init(freq=2)

        @cmemgr.map_to_thread(tim.callback)
        def led_blink():
            with Indicator(1):
                pyb.delay(10)

    @utest.cond(equals(3))
    def test_mapper_multi_interrupts(self):
        TiTuple = namedtuple('TiTuple', ('tim', 'id'))
        for info in [TiTuple(pyb.Timer(tim_id, freq=tim_id + 1), tim_id) for tim_id in (1, 2, 4)]:
            @cmemgr.map_to_thread(info.tim.callback, info.id)
            def led_blink(led_id):
                with Indicator(led_id):
                    pyb.delay(10)


if __name__ == '__main__':
    print('tests list:')
    print('1. test for single thread')
    print('2. test for single interrupt')
    print('3. test for multi interrupts')
    x = int(input('please choose one: '))
    utest.main(x)
