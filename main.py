import pyb
import cmemgr
import syncpri
import _thread


spin_mutex = None

# test for SpinMutex
def test_spin_mutex():
    global spin_mutex
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
                pyb.delay(50)

    _thread.start_new_thread(thread1, [])
    _thread.start_new_thread(thread2, [])


