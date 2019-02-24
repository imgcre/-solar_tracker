import utest
import syncpri


class MyOwnClass(utest.TestCase):
    def test_func1(self):
        pass

    def __private_func(self):
        pass

    @staticmethod
    @utest.ignore
    def static_func():
        print('It`s a static method')
        pass
    pass


class AnotherClass(utest.TestCase):
    pass


def main():
    utest.main()
