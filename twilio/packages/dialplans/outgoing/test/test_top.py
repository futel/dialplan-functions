import unittest
import top

xml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Hello World</Say></Response>'


class TestTop(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(top.top(None)['body'], xml)


if __name__ == '__main__':
    unittest.main()
