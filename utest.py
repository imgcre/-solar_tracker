import sys


class TestCase(object):
    def assert_equal(self, a, b):
        # raise error when cond is not satisfied
        pass


# your test suit file should be the main module
def main():
    main_module = __import__('__main__')
    for test_case in __get_attrs_form(main_module,
      where=lambda attr: type(attr) is type and issubclass(attr, TestCase)):
        # check the target class
        # create a instance for the class
        # and call its all method by that instance
        # use callable() to detect whether a attr is a function
        # type??
        print('on class', test_case.__name__, ':')
        inst = test_case()
        for test_func in __get_attrs_form(test_case,
          where=lambda attr: callable(attr) and not attr.__name__.startswith('__')):
            print('found func:', test_func.__name__)



def __get_attrs_form(obj, *, where=None):
    attr_iter = map(lambda attr_name: getattr(obj, attr_name), dir(obj))
    if where is not None and callable(where):
        attr_iter = filter(where, attr_iter)
    return attr_iter
