import pyb
import _thread
from cmemgr import map_to_thread, Mapper


def partial(func):
    def wrapper1(*args, **kwargs):
        def wrapper2(*args_, **kwargs_):
            kwargs_.update(kwargs)
            return func(*args + args_, **kwargs_)
        return wrapper2
    return wrapper1


# TODO: 直接用装饰器不好吗
# 用于创建代理模式的工具函数
# NOTE: 在类作用域内无法使用类名, 但此时locals()指向类作用域, 修改locals()可以操作类变量
def map_methods(locals_, src_cls, mapper, *, exclude=()):
    src_attrs = ((getattr(src_cls, attr_name), attr_name) for attr_name in dir(src_cls)
                 if attr_name not in exclude + ('__init__', '__class__'))
    for method, name in (attr_info for attr_info in src_attrs if callable(attr_info[0])):
        locals_[name] = mapper(method)


class ObjLike(object):
    # @staticmethod  # 使用此装饰器会造成方法无法调用
    def mapper(method):
        def func(self, *args, **kwargs):
            res = method(self.__dict, *args, **kwargs)
            return res if type(res) is not dict else ObjLike(res)
        return func

    map_methods(locals(), dict, mapper)

    def __init__(self, dict_=None):
        super().__init__()
        self.__dict = dict_ if dict_ is not None else {}

    def __repr__(self):
        return self.__dict

    def __getattr__(self, item):
        if self.__dict.get(item) is None:
            self.__dict[item] = {}
        return self.__dict[item] if type(self.__dict[item]) is not dict else ObjLike(self.__dict[item])

    def __setattr__(self, key, value):
        if key == '__dict':
            super().__setattr__(key, value)
        else:
            self.__dict[key] = value


# FIXME: 形如: x = tls.xxx, x.yyy = zzz 的代码可能会引入不确定的行为
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


class Indicator(pyb.LED):
    __nested_times = dict()
    __indicator_owners = dict()

    # TODO: const
    def __init__(self, led_id=2):
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


class STRegItem:
    def __init__(self, cb, freq, owner):
        self.cb, self.freq, self.owner = cb, freq, owner
        self.__target_val = 1 / freq
        self.__cur_val = 0

    def update(self, step):
        self.__cur_val += step
        for _ in range(int(self.__cur_val / self.__target_val)):
            self.cb()
        self.__cur_val %= self.__target_val

    def dispose(self):
        self.owner.unregister(self)


class SoftTimer:
    __base_freq = 100  # 这里频率一高会有问题
    __softtimer_map = {}

    @classmethod
    def make(cls, timer_id: int = 1):
        return SoftTimer(timer_id) if cls.__softtimer_map.get(timer_id) is None else cls.__softtimer_map[timer_id]

    def __callback(self):
        for item in self.__reg_items:
            item.update(self.__step)

    # 请不要在外部调用构造函数
    def __init__(self, timer_id: int = 1):
        if type(self).__softtimer_map.get(timer_id) is None:
            self.__tim = pyb.Timer(timer_id, freq=type(self).__base_freq)
            self.__step = 1 / type(self).__base_freq
            self.__reg_items = []

            self.__mapper = Mapper(self.__tim.callback, self.__callback, nargs=1, forward_args=False)
            type(self).__softtimer_map[timer_id] = self
        else:
            raise AssertionError

    @classmethod
    def default_register(cls, cb, freq):
        cls.make().register(cb, freq)

    @classmethod
    def default_unregister(cls, item):
        cls.make().unregister(item)

    def register(self, cb, freq):
        new_item = STRegItem(cb, freq, self)
        self.__reg_items.append(new_item)
        return new_item

    def unregister(self, item: STRegItem):
        if item not in self.__reg_items:
            raise ValueError
        self.__reg_items.remove(item)


# 可以设置预期时间(单位为毫秒)刷新速度和最大速度
# 最大速度的优先级高于预期时间
# refresh_rate
# max_speed = -1, 则不限速
# max_speed表示每毫秒的速度
# expected_duration 单位为毫秒
class Tween:
    def __init__(self, *, init_val=0, target_val=None, refresh_rate=50, allow_float=False, max_speed=-1, expected_duration, percentage=0, auto_tick=True):
        self.__refresh_rate, self.__allow_float, self.__max_speed, self.__expected_duration = refresh_rate, allow_float, max_speed, expected_duration

        self.__cur_val = init_val
        self.__target_val, self.__speed = None, None
        self.__on_updated, self.__on_completed = None, None
        self.set_target(self.__cur_val if target_val is None else target_val)
        if percentage > 0 and target_val:
            self.__cur_val = init_val + (target_val - init_val) * percentage

        if auto_tick:
            self.__item = SoftTimer.make().register(self.__callback, refresh_rate)

    def tick(self):
        self.__callback()

    def __callback(self):
        if self.__speed != 0:
            next_val = self.__cur_val + self.__speed * 1000 / self.__refresh_rate
            if (self.__speed > 0 and next_val >= self.__target_val) or (
                    self.__speed < 0 and next_val <= self.__target_val):
                next_val = self.__target_val
                self.__speed = 0
                if self.on_updated is not None:
                    self.on_updated(next_val if self.__allow_float else int(next_val))
                if self.on_completed is not None:
                    self.on_completed()
            elif self.__allow_float or int(self.__cur_val) is not int(next_val):
                if self.on_updated is not None:
                    self.on_updated(next_val if self.__allow_float else int(next_val))
            self.__cur_val = next_val

    @property
    def on_updated(self):
        return self.__on_updated

    @on_updated.setter
    def on_updated(self, value):
        self.__on_updated = value

    @property
    def on_completed(self):
        return self.__on_completed

    @on_completed.setter
    def on_completed(self, value):
        self.__on_completed = value

    @property
    def cur_value(self):
        return self.__cur_val

    def set_target(self, target_val, *, expected_duration=None):
        self.__target_val = target_val
        if expected_duration is not None:
            self.__expected_duration = expected_duration
        # 每毫秒步长
        self.__speed = (target_val - self.__cur_val) / self.__expected_duration
        if (self.__max_speed > 0) and (self.__speed > self.__max_speed):
            self.__speed = self.__max_speed

