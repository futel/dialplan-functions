from unittest import mock, TestCase
import urllib

from chalicelib import env_util
from chalicelib import util


env = {'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
       'ASSET_HOST': 'ASSET_HOST',
       'stage': 'stage',
       'extensions': {
           "test-one": {
               "outgoing": "outgoing_safe",
               "caller_id": "+19713512383",
               "enable_emergency": False
           }}}


class TestUtil(TestCase):

    def test_normalize_number(self):
        self.assertEqual(util.normalize_number('+15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('5035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+911'), '+1911')
        self.assertEqual(util.normalize_number('911'), '+1911')

    def test_e164_to_extensions(self):
        extensions = env_util._get_extensions()
        self.assertEqual(
            util.e164_to_extensions('+15034449412', extensions), ['ainsworth'])

    def test_filter_outgoing_number(self):
        self.assertFalse(util.filter_outgoing_number('+1911', True))
        self.assertFalse(util.filter_outgoing_number('+15035551212', True))
        # Mexico City Anthropological Museum
        self.assertFalse(
            util.filter_outgoing_number('+525555536266', True))

    def test_dial_pstn(self):
        extensions = env_util._get_extensions()
        extension = extensions['ainsworth']
        request = mock.Mock(
            headers={'host': 'host'},

            query_params={},
            post_fields={
                'SipDomain':'direct-futel-prod.sip.twilio.com'})
        response = util.dial_pstn(
            '+15035551212',
            extension,
            request)
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response>'
            '<Dial action="/ops/call_status_outgoing" '
            'answerOnBridge="true" callerId="+15034449412" timeLimit="3600">'
            '<Number>+15035551212</Number></Dial></Response>')

    def test_dial_sip_asterisk(self):
        response = util.dial_sip_asterisk('#', 'test-one', env)
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial answerOnBridge="true" timeLimit="3600"><Sip>sip:outgoing_safe@futel-stage.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>')

    def test_function_url_no_params(self):
        self.assertEqual(util.function_url('/foo'), '/foo')

    def test_function_url_with_params(self):
        url = util.function_url('/foo', [('a', '1'), ('b', '2')])
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        # parse_qs returns lists for values
        self.assertEqual(qs, {'a': ['1'], 'b': ['2']})

    def test_function_url_omits_none(self):
        url = util.function_url('/foo', [('a', '1'), ('b', None)])
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(qs, {'a': ['1']})

    def test_function_url_encodes(self):
        url = util.function_url('/search', [('q', 'a b'), ('x', '@')])
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(qs, {'q': ['a b'], 'x': ['@']})

    def test_function_url_param_with_two_values(self):
        url = util.function_url('/foo', [['foo', 'bar'], ['foo', 'baz']])
        self.assertEqual(url, '/foo?foo=bar&foo=baz')


if __name__ == '__main__':
    unittest.main()
