
def init_for(*modules):
    for module in modules:
        for static_deco in (staticmethod, classmethod):
            setattr(module, static_deco.__name__, __decorator(static_deco))


def is_static_method(func):
    return hasattr(func, '__is_static__')


def __decorator(origin):
    def static_wrapper(func):
        return origin(__StaticMethodWrapper(func))
    return static_wrapper


class __StaticMethodWrapper:
    # since @classmethod may cause a bound method we will test for
    # but inherit the attr that the class has created
    # we should add a attr to detect whether a method is static
    # otherwise, find a way to unbind it :)
    __is_static__ = None

    def __init__(self, func):
        self.__func = func
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        self.__func(*args, **kwargs)
