

def init_for(*modules):
    for module in modules:
        setattr(module, 'staticmethod', __decorator)


def __decorator(func):
    return staticmethod(__StaticWrapper(func))


class __StaticWrapper:
    __is_static__ = None

    def __init__(self, func):
        self.__func = func

    def __call__(self, *args, **kwargs):
        self.__func(*args, **kwargs)
