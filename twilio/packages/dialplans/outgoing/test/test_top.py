import unittest
import top


class TestTop(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(top.top(None)['body'], top.xml)


if __name__ == '__main__':
    unittest.main()
