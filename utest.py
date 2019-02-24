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
    # globals()'s return val is mutable

    # TODO: get the module which called this function
    # use dir() to get all attr from a module!
    main_module = __import__('__main__')
    main_attr_iter = list(map(lambda attr_name: getattr(main_module, attr_name), dir(main_module)))
    print(main_attr_iter)
    for test_case in filter(lambda attr: isinstance(attr, TestCase), main_attr_iter):
        print(test_case)

