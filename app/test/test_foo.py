from unittest import mock, TestCase

import app


class TestFoo(TestCase):

    def test_foo(self):
        self.assertEqual('foo', app.index())


if __name__ == '__main__':
    unittest.main()
