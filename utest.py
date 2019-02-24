import sys


class TestCase(object):
    def assert_equal(self, a, b):
        # raise error when cond is not satisfied
        pass


# your test suit file should be the main module
def main():
    base_class_func_names = list(map(lambda func: func.__name__, __get_method_from(TestCase)))
    main_module = __import__('__main__')
    for test_case in __get_attrs_form(main_module,
      where=lambda attr: type(attr) is type and issubclass(attr, TestCase)):
        # check the target class
        # create a instance for the class
        # and call its all method by that instance
        # use callable() to detect whether a attr is a function
        # type?? caused by __class__ attr
        print('on class', test_case.__name__, ':')
        inst = test_case()
        for test_func in __get_method_from(test_case,
          where=lambda func: func.__name__ not in base_class_func_names):
            print('found func:', test_func.__name__)
        else:
            print('found nothing :)')


def __get_method_from(cls, *, where=lambda t: True):
    return __get_attrs_form(cls,
      where=lambda attr: callable(attr)
        and not attr.__name__.startswith('__')
        and attr.__name__ not in ['type']
        and where(attr))


def __get_attrs_form(obj, *, where=None):
    attr_iter = map(lambda attr_name: getattr(obj, attr_name), dir(obj))
    if where is not None and callable(where):
        attr_iter = filter(where, attr_iter)
    return attr_iter
