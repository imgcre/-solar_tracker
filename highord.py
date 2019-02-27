
def equals(a):
    def func(x):
        return __resolve(x, a)[0] == x
    return func


# get item from tuple or list
# usage: get_item(index)(action)
# where action is callable to handle the item or raise an error
# eg: get_item(0)(get_item(0)(///))
# TODO: items[0]()
def get_item(index, action):
    def func(x):
        # TODO: assert
        return action(x[__resolve(x, index)[0]])
    return func


# if arg form args is callable, call arg with x as param
# then replace it by the result
def __resolve(x, *args):
    args = list(args)
    for i in range(len(args)):
        while callable(args[i]):
            args[i] = args[i](x)
    return args
