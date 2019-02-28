from highord import *


# if called a high ord func, return a wrapper of it
# DSLMaker = type('DSLMaker', (object,))
def make_this():
    attrs = dict()
    # just simply return obj itself
    attrs['__call__'] = lambda self, obj: obj
    return type('DSLMaker', (object,), attrs)


this = make_this()


class DSLBuilder:
    def __init__(self):
        self.__method_chain = []

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
            return self
        else:
            def wrapper(*args):
                self.__method_chain.append(func(*args))
                return self
            return wrapper

    pass
