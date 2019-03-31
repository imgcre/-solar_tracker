from utilities import ThreadLocalStorage, ObjLike


class Context:
    def __init__(self, *, enter_func=None, exit_func=None):
        self.__nest_count = 0
        self.__enter_func = enter_func
        self.__exit_func = exit_func
        self.arg_chain = []
        self.__cur_args = None
        self.cur_args = None

    def __enter__(self):
        self.arg_chain.append(self.__cur_args)
        self.cur_args = self.__cur_args
        self.__cur_args = None
        self.__nest_count += 1
        if self.__enter_func is not None:
            self.__enter_func()

    def __exit__(self, *args):
        self.arg_chain.pop()
        self.cur_args = self.arg_chain[-1] if len(self.arg_chain) > 0 else None
        self.__nest_count -= 1
        if self.__exit_func is not None:
            self.__exit_func()

    def __call__(self, *args, **kwargs):
        self.__cur_args = (args, kwargs)
        return self

    @property
    def nest_count(self):
        return self.__nest_count

    pass
