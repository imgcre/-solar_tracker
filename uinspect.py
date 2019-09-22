import sys


main_module = __import__('__main__')


def is_public_method(attr):
    return callable(attr) and not attr.__name__.startswith('__') and attr.__name__ not in ['type']


# return False if obj is not an inst of class
def is_inherit_from(obj, cls):
    return type(obj) is type and issubclass(obj, cls)


def enable_static_method_detect(*modules):
    for module in ((__import__(mod) if type(mod) is str else mod for mod in modules)
                   if len(modules) else [main_module] + list(sys.modules.values())):
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
