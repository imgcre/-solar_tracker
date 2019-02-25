import utest
import syncpri


class MyOwnClass(utest.TestCase):
    x = 0

    def __init__(self):
        self.x = 233

    def test_func1(self):
        print('self.x =', self.x)
        self.x = 5
        print('setup x`s val')

    def test_func2(self):
        print('self.x =', self.x)

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
