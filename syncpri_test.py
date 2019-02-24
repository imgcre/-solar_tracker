import utest
import syncpri


class MyOwnClass(utest.TestCase):
    def test_func1(self):
        pass
    def __private_func(self):
        pass
    pass


class AnotherClass(utest.TestCase):
    pass


def main():
    utest.main()
