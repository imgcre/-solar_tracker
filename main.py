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

m = None
x = 1.1
tim = pyb.Timer(1)
def test_mapper():
    global m
    tim.init(freq=1)

    def func():
        global x
        x += 0.2
        print(x)

    m = cmemgr.Mapper(tim.callback, func, nargs=1, forward_args=False)

