from unittest import mock, TestCase

from chalicelib import env_util
from chalicelib import util

env = {'AWS_TOPIC_ARN': 'AWS_TOPIC_ARN',
       'ASSET_HOST': 'ASSET_HOST',
       'extensions': {
           "test": {
               "outgoing": "outgoing_safe",
               "caller_id": "+19713512383",
               "enable_emergency": False,
               "local_outgoing": True
           }}}


class TestUtil(TestCase):

    def test_function_url(self):
        request = mock.Mock()
        request.headers = {'host': 'host'}
        request.post_fields = {
            'SipDomain': 'direct-futel-prod.sip.twilio.com'}
        self.assertEqual(
            util.function_url(request, 'foo'),
            'https://host/foo')

    def test_normalize_number(self):
        self.assertEqual(util.normalize_number('+15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('15035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('5035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('01115035551212'), '+15035551212')
        self.assertEqual(util.normalize_number('+911'), '+1911')
        self.assertEqual(util.normalize_number('911'), '+1911')

    def test_e164_to_extension(self):
        extensions = env_util.get_extensions()
        self.assertEqual(
            util.e164_to_extension('+19713512383', extensions), 'test-one')

    def test_filter_outgoing_number(self):
        self.assertFalse(util.filter_outgoing_number('+911', True))
        self.assertFalse(util.filter_outgoing_number('+15035551212', True))
        # Mexico City Anthropological Museum
        self.assertFalse(
            util.filter_outgoing_number('+525555536266', True))

    def test_dial_pstn(self):
        request = mock.Mock(
            headers={'host': 'host'},
            query_params={},
            post_fields={
                'SipDomain':'direct-futel-prod.sip.twilio.com'})
        response = util.dial_pstn(
            '+15035551212',
            'sip:test@direct-futel-nonemergency-stage.sip.twilio.com',
            request,
            env)
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response>'
            '<Dial action="https://host/metric_dialer_status" '
            'answerOnBridge="true" callerId="+19713512383">'
            '<Number>+15035551212</Number></Dial></Response>')

    def test_dial_sip(self):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'},
        context={'domainPrefix':'prod'})
        response = util.dial_sip_asterisk('#', request, env)
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true"><Sip>sip:outgoing_safe@futel-prod.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>')


if __name__ == '__main__':
    unittest.main()
