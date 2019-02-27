
def equals(a):
    def func(x):
        return __resolve(x, a)[0] == x
    return func


def __resolve(x, *args):
    args = list(args)
    for i in range(len(args)):
        while callable(args[i]):
            args[i] = args[i](x)
    return args
    pass
