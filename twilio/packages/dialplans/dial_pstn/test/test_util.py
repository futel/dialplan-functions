from unittest import mock, TestCase
import util

class TestUtil(TestCase):

    def test_get_extensions(self):
        self.assertTrue(util.get_extensions())

if __name__ == '__main__':
    unittest.main()
