
def equals(a):
    def func(x):
        return __resolve(x, a)[0] == x
    return func


def not_(a):
    def func(x):
        return not __resolve(x, a)[0]
    return func


# get item from tuple or list
# usage: get_item(index)(action)
# where action is callable to handle the item or raise an error
# eg: get_item(0)(get_item(0)(///))
def get_item(index):
    def actor(action):
        def func(obj):
            # TODO: assert
            return action(obj[__resolve(obj, index)[0]])  # obj的类型是int
        return func
    return actor


# TODO: support for dict
def get_attr(item):
    def actor(action):
        def func(obj):
            if type(obj) is not dict:
                return action(getattr(obj, __resolve(obj, item)[0]))
            else:
                pass
            pass
        return func
    return actor


# if arg form args is callable, call arg with x as param
# then replace it by the result
def __resolve(x, *args):
    args = list(args)
    for i in range(len(args)):
        args[i] = args[i](x)
    return args
