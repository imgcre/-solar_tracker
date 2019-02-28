from highord import *


class DSLBuilder:
    def __init__(self, *, other=None, func=None, terminal=True):
        if other is None:
            self.__method_chain = []
        else:
            self.__method_chain = other.__method_chain + [func]
        self.__terminal = terminal

    def __call__(self, obj):
        chain_len = len(self.__method_chain)
        if chain_len:
            func = self.__method_chain[chain_len - 1]
            if not self.__terminal:
                func = func(lambda t: t)
            for i in range(chain_len - 1):
                func = self.__method_chain[chain_len - i - 2](func)
            return func(obj)
        else:
            return obj

    def __getattr__(self, item):
        return DSLBuilder(other=self, func=get_attr(item), terminal=False)

    def __getitem__(self, item):
        return DSLBuilder(other=self, func=get_item(item), terminal=False)

    def __eq__(self, other):
        # return a closure that return self
        # forward the args to equals
        return self.__make_wrapper(equals(other), called=True)

    def __make_wrapper(self, func, *, called=False):
        if called:
            return DSLBuilder(other=self, func=func)
        else:
            def wrapper(*args):
                return DSLBuilder(other=self, func=func(*args))
            return wrapper

    pass

# and some others method for dsl-builder


this = DSLBuilder()

