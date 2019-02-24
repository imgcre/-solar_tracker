import utest
import syncpri


@utest.ignore
def dummy():
    pass


class MyOwnClass(utest.TestCase):
    def test_func1(self):
        pass

    def __private_func(self):
        pass

    @staticmethod
    def static_func():
        print('It`s a static method')
        pass
    pass


class AnotherClass(utest.TestCase):
    pass


def main():
    utest.main()
