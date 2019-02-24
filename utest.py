import sys

# find all method in the inherited class
class TestCase(object):
    def __init__(self):
        # do not write code here
        # we use another file to contain the test code
        # we can use callable function to detect if a object is a function
        pass
    pass


def main():
    # when this file is as
    # we can use globals() to get all class
    # seems that globals() can only get the variables that in its own module

    # TODO: get the module which called this function
    # use dir() to get all attr from a module!

    return lambda: print(globals())
