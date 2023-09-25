from unittest import mock, TestCase

from chalicelib import env_util

class TestUtil(TestCase):

    def test_get_extensions(self):
        self.assertTrue(env_util.get_extensions().keys())

    def test_get_ivrs(self):
        self.assertTrue(env_util.get_ivrs().keys())


if __name__ == '__main__':
    unittest.main()
