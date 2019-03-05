import pyb
import _thread


# TODO try to invoke super().__setattr__()
class ObjLike(dict):
    def __getattr__(self, item):
        pass

    def __setattr__(self, key, value):
        super(ObjLike, self).__setattr__(key, value)


class Indicator(pyb.LED):
    __nested_times = dict()
    __indicator_owners = dict()

    # TODO: const
    def __init__(self, led_id):
        super().__init__(led_id)
        self.__led_id = led_id
        owner = type(self).__indicator_owners.get(led_id)
        if owner is not None:
            raise RuntimeError('led' + str(led_id) + ' is occupied by thread-' + str(owner))

    def __enter__(self):
        thread_id = _thread.get_ident()
        type(self).__indicator_owners[self.__led_id] = thread_id
        if type(self).__nested_times.get(self.__led_id) is None:
            type(self).__nested_times[self.__led_id] = 1
            self.on()
        else:
            type(self).__nested_times[self.__led_id] += 1
            for _ in range(max(type(self).__nested_times[self.__led_id], 3)):
                self.off()
                pyb.delay(50)
                self.on()
                pyb.delay(50)

    def __exit__(self, *args):
        thread_id = _thread.get_ident()
        assert thread_id is type(self).__indicator_owners[self.__led_id]
        type(self).__indicator_owners.pop(self.__led_id)
        type(self).__nested_times[self.__led_id] -= 1
        if type(self).__nested_times[self.__led_id] is 0:
            type(self).__nested_times.pop(self.__led_id)
            self.off()
        else:
            for _ in range(max(type(self).__nested_times[self.__led_id] + 1, 3)):
                self.off()
                pyb.delay(25)
                self.on()
                pyb.delay(25)


class ExitLoop(Exception):
    pass


def infinite_loop_thread(f):
    infinite_loop_thread_for(None)(lambda t: f())
    return f


def infinite_loop_thread_for(*args):
    def wrapper(f):
        def func(arg):
            try:
                while True:
                    f(arg)
            except ExitLoop:
                pass
        [_thread.start_new_thread(func, [arg]) for arg in args]
        return f
    return wrapper
