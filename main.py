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
#   freq = 1: 52%
#   freq = 50: 54%
#   freq = 100: 52%

# test for the thread mode


def test_mapper_multi_interrupt(freq1=50, freq2=80):
    global m1, m2, star_var, star_dir, sharp_var, sharp_dir
    tim1 = pyb.Timer(1)
    tim2 = pyb.Timer(2)
    tim1.init(freq=freq1)
    tim2.init(freq=freq2)
    star_var, sharp_var = None, None
    def star_animate():
        global star_var, star_dir
        if star_var is None:
            star_var = ''
            star_dir = False

        if not star_dir:
            star_var += '*'
            if len(star_var) >= 10:
                star_dir = True
        else:
            star_var = star_var[:-1]
            if len(star_var) == 0:
                star_dir = False

        print(star_var)

        pass

    def sharp_animate():
        global sharp_var, sharp_dir
        if sharp_var is None:
            sharp_var = ''
            sharp_dir = False

        if not sharp_dir:
            sharp_var += '#'
            if len(sharp_var) >= 10:
                sharp_dir = True
        else:
            sharp_var = sharp_var[:-1]
            if len(sharp_var) == 0:
                sharp_dir = False

        print(sharp_var)


        pass

    m1 = cmemgr.Mapper(tim1.callback, star_animate, nargs=1, forward_args=False)
    m2 = cmemgr.Mapper(tim2.callback, sharp_animate, nargs=1, forward_args=False)

m = None
x = 0
y = 0
tim = pyb.Timer(1)
def test_mapper_interrpt(freq=10):
    global m
    tim.init(freq=freq)

    def func():
        global x
        x += 1
        if x % 10 == 0:
            print(x, '/', y)

    def int_func():
        global y
        y += 1

    m = cmemgr.Mapper(tim.callback, func, interrpt_func=int_func, nargs=1, forward_args=False)


wrapper = None

def test_mapper_thread():
    global m


    def caller(func):
        global wrapper
        wrapper = func

    def my_func():
        print('func being called!')

    m = cmemgr.Mapper(caller, my_func)

    pass

