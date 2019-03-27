from utilities import ThreadLocalStorage, ObjLike


class Context:
    def __init__(self, *, enter_func=None, exit_func=None):
        self.__tls = ObjLike()  # ThreadLocalStorage()
        self.__tls.nest_count = 0
        self.__enter_func = enter_func
        self.__exit_func = exit_func

    def __enter__(self):
        self.__tls.nest_count += 1
        if self.__enter_func is not None:
            self.__enter_func()

    def __exit__(self, *args):
        self.__tls.nest_count -= 1
        if self.__exit_func is not None:
            self.__exit_func()

    @property
    def nest_count(self):
        return self.__tls.nest_count

    pass
