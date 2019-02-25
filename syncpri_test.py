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


class Base:
    x = 0
    
    @classmethod
    def test_func(cls):
        cls.x += 1


class Child(Base):
    def inst_test(self):
        self.test_func()


def main():
    utest.main()
