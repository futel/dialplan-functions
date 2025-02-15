from unittest import mock, TestCase

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

    def test_e164_to_extension(self):
        extensions = env_util._get_extensions()
        self.assertEqual(
            util.e164_to_extension('+19713512383', extensions), 'test-one')

    def test_filter_outgoing_number(self):
        self.assertFalse(util.filter_outgoing_number('+1911', True))
        self.assertFalse(util.filter_outgoing_number('+15035551212', True))
        # Mexico City Anthropological Museum
        self.assertFalse(
            util.filter_outgoing_number('+525555536266', True))

    def test_dial_pstn(self):
        extensions = env_util._get_extensions()
        extension = extensions['test-one']
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
            'answerOnBridge="true" callerId="+19713512383" timeLimit="3600">'
            '<Number>+15035551212</Number></Dial></Response>')

    def test_dial_sip_asterisk(self):
        response = util.dial_sip_asterisk('#', 'test-one', env)
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial answerOnBridge="true" timeLimit="3600"><Sip>sip:outgoing_safe@futel-stage.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>')


if __name__ == '__main__':
    unittest.main()
