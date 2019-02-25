import utest
import syncpri


class MyOwnClass(utest.TestCase):

    def test_func1(self):
        self.assert_equal(1, 2)

    def test_func2(self):
        self.assert_equal(3, 4)


class AnotherClass(utest.TestCase):

    def another_test(self):
        self.assert_equal(5, 5)

    def another_test2(self):
        self.assert_equal(6, 7)


def main():
    utest.main()
