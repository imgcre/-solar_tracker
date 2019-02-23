import pyb
import cmemgr
import syncpri
import _thread


# test for SpinMutex
def test_spin_mutex():
    spin_mutex = syncpri.SpinMutex()

    def thread1():
        while True:
            with spin_mutex:
                pyb.LED(1).off()
                pyb.delay(500)
            pyb.delay(500)

    def thread2():
        while True:
            with spin_mutex:
                pyb.LED(1).on()
                pyb.delay(50)
                pyb.LED(1).off()
            pyb.delay(50)  # for thread switch

    _thread.start_new_thread(thread1, [])
    _thread.start_new_thread(thread2, [])

# using critical section:
#   freq = 1: 52%
#   freq = 50: 52%
#   freq = 100: 53%

# without using critical section:
#   freq = 1:

m = None
x = 0
y = 0
tim = pyb.Timer(1)
def test_mapper(freq=100):
    global m
    tim.init(freq=freq)

    def func():
        global x
        x += 1
        print(x, '/', y)

    def int_func():
        global y
        y += 1

    event = syncpri.Event(mutex=syncpri.SpinMutex(restrict_owner=False, using_critical_section=False))
    m = cmemgr.Mapper(tim.callback, func, interrpt_func=int_func, nargs=1, forward_args=False, event=event)

