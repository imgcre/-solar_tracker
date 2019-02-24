import utest
import syncpri


class MyOwnClass(utest.TestCase):
    x = 0

    def test_func1(self):
        pass

    def __private_func(self):
        pass

    @staticmethod
    def static_func():
        print('It`s a static method')
        pass
    pass

    @classmethod
    def change_x_to(cls, val):
        cls.x = val


class AnotherClass(utest.TestCase):
    pass


def main():
    utest.main()
