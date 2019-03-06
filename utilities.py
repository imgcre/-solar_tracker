import pyb
import _thread


class ObjLike(dict):
    def __init__(self, dict_):
        super().__init__()
        self.__dict = dict_ if dict_ is not None else {}

    def __getattr__(self, item):
        return self.__dict[item]

    def __setattr__(self, key, value):
        if key == '__dict':
            super().__setattr__(key, value)
        else:
            self.__dict[key] = value


# __locals = {}


class ThreadLocalStorage(object):
    __locals = {}

    def __get__(self, instance, owner):
        print('get tls')
        thread_id = _thread.get_ident()
        if type(self).__locals.get(thread_id) is None:
            type(self).__locals[thread_id] = {}
        return ObjLike(type(self).__locals[thread_id])

    
tls = ThreadLocalStorage()

# def __getattr__(key):  # do not from ... import tls
#    tls 根据不同的线程返回不同的包装对象
#    if key == 'tls':
#        print('get tls')
#        thread_id = _thread.get_ident()
#       if __locals.get(thread_id) is None:
#           __locals[thread_id] = {}
#       return ObjLike(__locals[thread_id])
#  else:
#      raise AttributeError


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
