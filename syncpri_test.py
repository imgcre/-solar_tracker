import utest
import syncpri


class MyOwnClass(utest.TestCase):

    def test_func1(self):

        pass

    def test_func2(self):
        self.assert_equal(1, 2)
        pass


def main():
    utest.main()
