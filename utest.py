import sys
import uinspect

# init the ability to detect static method for main module
uinspect.enable_static_method_detect(uinspect.main_module)


class TestCase(object):
    def assert_equal(self, a, b):
        if a != b:
            raise TestError(str(a) + ' is not equal to ' + str(b))


class TestError(Exception):
    pass


# return a wrapper that has a function attr names __utest_cond__
def cond(cond_expr):
    def func(f):
        return CondWrapper(f, cond_expr)
    return func
    pass


class CondWrapper:
    def __init__(self, func, cond_expr):
        self.__func = func
        self.__name__ = func.__name__
        self.__cond_expr__ = cond_expr

    def __call__(self, *args, **kwargs):
        self.__func(args, kwargs)


# NOTE: your test cases should be in the main module
# if cond is specified, only call methods which is satisfied the cond
def main(cond=None):
    # base_class_func_names = list(map(lambda func: func.__name__, __get_method_from(TestCase)))
    base_class_func_names = [func.__name__ for func in __get_target_method_from(TestCase)]

    for test_case in (attr for attr in __get_attrs_form(uinspect.main_module)
                      if uinspect.is_inherit_from(attr, TestCase)):
        # find the target classes
        # create an instance for each of the classes
        # and call its inst methods
        error_raised = False
        inst = test_case()

        for test_func in (func for func in __get_target_method_from(test_case)
                          if func.__name__ not in base_class_func_names and (
                cond is None or not hasattr(func, '__cond_expr__') or getattr(func, '__cond_expr__')(cond))):
            try:
                test_func(inst)
            except TestError as t:
                if not error_raised:
                    error_raised = True
                    print('at', test_case.__name__ + ':')
                print('  at', test_func.__name__ + ':', *t.args)


def __get_target_method_from(cls):
    return (attr for attr in __get_attrs_form(cls)
            if uinspect.is_public_method(attr) and not uinspect.is_static_method(attr))


def __get_attrs_form(obj):
    return (getattr(obj, attr_name) for attr_name in dir(obj))
