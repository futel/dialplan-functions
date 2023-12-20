from unittest import mock, TestCase

from chalicelib import env_util
from chalicelib import ivr_destinations

request = mock.Mock(
    context={'domainPrefix':'domainPrefix'},
    headers={'host': 'host'},
    post_fields={'From':'From'})

env = {'extensions': env_util.get_extensions(), 'operator_numbers':['foo', 'bar']}

class TestIvrsDestinations(TestCase):

    def test_pre_callable_missing(self):
        self.assertTrue(
            ivr_destinations.outgoing_operator_enqueue(request, env))


if __name__ == '__main__':
    unittest.main()
