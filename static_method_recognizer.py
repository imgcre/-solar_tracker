
def init_for(*modules):
    for module in modules:
        for static_deco in (staticmethod, classmethod):
            setattr(module, static_deco.__name__, __decorator(static_deco))


def __decorator(origin):
    def static_wrapper(func):
        return origin(__StaticWrapper(func))
    return static_wrapper


class __StaticWrapper:
    __is_static__ = None

    def __init__(self, func):
        self.__func = func

    def __call__(self, *args, **kwargs):
        self.__func(*args, **kwargs)
