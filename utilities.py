import pyb
import _thread


# todo: add support for recursive
# add multi thread support
# blink n times when enter the n recursive, up to 5
# blink once when exit recursive
class Indicator(pyb.LED):
    def __enter__(self):
        self.on()

    def __exit__(self, *args):
        self.off()
    pass


class ExitLoop(Exception):
    pass


def infinite_loop(func):
    def wrapper(*args, **kwargs):
        try:
            while True:
                func(*args, **kwargs)
        except ExitLoop:
            pass
    return wrapper
