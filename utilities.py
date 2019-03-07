import pyb
import _thread


# 包装器
def map_methods(dst_cls, src_cls, mapper, *, exclude=('__init__', '__class__')):
    src_attrs = ((getattr(src_cls, attr_name), attr_name) for attr_name in dir(src_cls) if attr_name not in exclude)
    for method, name in (attr_info for attr_info in src_attrs if callable(attr_info[0])):
        print(name)
        setattr(dst_cls, name, mapper(method))


class ObjLike(object):
    def __init__(self, dict_):
        super().__init__()
        self.__dict = dict_ if dict_ is not None else {}

    def __repr__(self):
        return self.__dict

    # TODO: 让外貌只是添加了额外语法支持的字典
    def __getattr__(self, item):
        if self.__dict.get(item) is None:
            self.__dict[item] = {}
        return self.__dict[item] if type(self.__dict[item]) is not dict else ObjLike(self.__dict[item])

    def __setattr__(self, key, value):
        if key == '__dict':
            super().__setattr__(key, value)
        else:
            self.__dict[key] = value


# Todo: dict method support
class ThreadLocalStorage(object):
    __locals = {}

    map_methods(locals(), ObjLike, lambda method:
                lambda self, *args, **kwargs: method(self.__get_obj(), *args, **kwargs))

    def __get_obj(self):
        thread_id = _thread.get_ident()
        if type(self).__locals.get(thread_id) is None:
            type(self).__locals[thread_id] = {}
        return ObjLike(type(self).__locals[thread_id])


tls = ThreadLocalStorage()


def get_attrs_form(obj):
    return (getattr(obj, attr_name) for attr_name in dir(obj))


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
