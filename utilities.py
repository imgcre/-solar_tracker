import pyb


# todo: add support for recursive
# add multi thread support
class Indicator(pyb.LED):
    def __enter__(self):
        self.on()

    def __exit__(self, *args):
        self.off()
    pass
