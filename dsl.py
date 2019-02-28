from highord import *


class DSLBuilder:
    def __init__(self, *, other=None):
        if other is None:
            self.__method_chain = []
        else:
            self.__method_chain = other.__method_chain.copy()

    def __call__(self, obj):
        chain_len = len(self.__method_chain)
        if chain_len:
            func = self.__method_chain[chain_len - 1]
            for i in range(chain_len - 1):
                func = self.__method_chain[chain_len - i - 2](func)
            return func(obj)
        else:
            return obj

    def __eq__(self, other):
        # return a closure that return self
        # forward the args to equals
        return self.__make_wrapper(equals(other), called=True)

    def __ne__(self, other):
        return self.__make_wrapper(not_(equals(other)), called=True)

    def __make_wrapper(self, func, *, called=False):
        if called:
            self.__method_chain.append(func)
            return DSLBuilder(other=self)
        else:
            def wrapper(*args):
                self.__method_chain.append(func(*args))
                return DSLBuilder(other=self)
            return wrapper

    pass


this = DSLBuilder()
