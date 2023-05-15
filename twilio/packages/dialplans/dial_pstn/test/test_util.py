from unittest import mock, TestCase

import util

class TestUtil(TestCase):

    def test_get_function_url(self):
        context = mock.Mock()
        context.api_host = 'https://host'
        context.namespace = 'namespace'
        self.assertEqual(
            util.function_url(context, 'foo'),
            'https://host/api/v1/web/namespace/dialplans/foo')
        self.assertEqual(
            util.function_url(context, 'foo', {'bar':'baz'}),
            'https://host/api/v1/web/namespace/dialplans/foo?bar=baz')

    def test_get_extensions(self):
        self.assertTrue(util.get_extensions())

    def test_normalize_number(self):
        self.assertEqual(util.normalize_number('+15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('5035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+911'), '+911')
        self.assertEqual(util.normalize_number('911'), '+911')

if __name__ == '__main__':
    unittest.main()
