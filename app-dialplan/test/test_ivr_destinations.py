from unittest import mock, TestCase

from chalicelib import env_util
from chalicelib import ivr_destinations

request = mock.Mock(
    context={'domainPrefix':'domainPrefix'},
    from_user='clinton',
    headers={'host': 'host'},
    post_fields={'From':'From'},
    query_params={'lang': 'en'})

env = {
    'ASSET_HOST':'ASSET_HOST',
    'extensions': env_util._get_extensions(),
    'operator_numbers':['foo', 'bar']}

class TestIvrsDestinations(TestCase):

    def test_pre_callable_missing(self):
        self.assertTrue(
            ivr_destinations.outgoing_operator_enqueue(request, env))

    def test_outgoing_dialtone_pre(self):
        self.assertTrue(
            ivr_destinations.outgoing_dialtone_pre(request, env))


if __name__ == '__main__':
    unittest.main()
