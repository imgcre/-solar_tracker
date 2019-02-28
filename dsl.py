from highord import *


# if called a high ord func, return a wrapper of it
# DSLMaker = type('DSLMaker', (object,))
def make_this():
    attrs = dict()
    # just simply return obj itself
    attrs['__call__'] = lambda self, obj: obj
    return type('DSLMaker', (object,), dict=attrs)


this = make_this()


class DSLBuilder:
    def __init__(self):
        self.__method_chain = []

    def __eq__(self, other):
        # return a closure that return self
        # forward the args to equals
        return self.__make_wrapper(equals(other), called=True)

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
