import sys
import uinspect as tt

# init the ability to detect static method for main module
tt.init_static_method_detect(tt.main_module)


class TestCase(object):
    def assert_equal(self, a, b):
        assert a == b, str(a) + 'is not equal to' + str(b)


class TestFault:
    pass

# NOTE: your test cases should be in the main module
def main():
    # base_class_func_names = list(map(lambda func: func.__name__, __get_method_from(TestCase)))
    base_class_func_names = [func.__name__ for func in __get_target_method_from(TestCase)]

    for test_case in (attr for attr in __get_attrs_form(tt.main_module)
                      if tt.is_inherit_from(attr, TestCase)):
        # find the target classes
        # create an instance for each of the classes
        # and call its inst methods
        print('on class', test_case.__name__, ':')
        inst = test_case()

        for test_func in (func for func in __get_target_method_from(test_case)
                          if func.__name__ not in base_class_func_names):
            print('found func:', test_func.__name__)
            test_func(inst)


def __get_target_method_from(cls):
    return (attr for attr in __get_attrs_form(cls)
            if tt.is_public_method(attr) and not tt.is_static_method(attr))


def __get_attrs_form(obj):
    return (getattr(obj, attr_name) for attr_name in dir(obj))
