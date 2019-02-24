import sys
from static_method_recognizer import init_for, is_static_method

# init the ability to detect static method for main module
init_for(__import__('__main__'))


class TestCase(object):
    def assert_equal(self, a, b):
        # TODO: raise error when cond is not satisfied
        pass


# NOTE: your test cases should be in the main module
def main():
    base_class_func_names = list(map(lambda func: func.__name__, __get_method_from(TestCase)))
    main_module = __import__('__main__')
    for test_case in __get_attrs_form(main_module,
      where=lambda attr: type(attr) is type and issubclass(attr, TestCase)):
        # find the target classes
        # create an instance for each of the classes
        # and call its inst methods
        print('on class', test_case.__name__, ':')
        inst = test_case()
        for test_func in __get_method_from(test_case,
          where=lambda func: not is_static_method(func) and func.__name__ not in base_class_func_names):
            print('found func:', test_func.__name__)


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
