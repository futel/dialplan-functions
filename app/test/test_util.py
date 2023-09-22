from unittest import mock, TestCase

from chalicelib import util

class TestUtil(TestCase):

    def test_get_extensions(self):
        self.assertTrue(util.get_extensions().keys())

    def test_get_ivrs(self):
        self.assertTrue(util.get_ivrs().keys())

    def test_twiml_response(self):
        self.assertTrue(util.twiml_response('foo').body, 'foo')

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
        extensions = util.get_extensions()
        self.assertEqual(
            util.e164_to_extension('+19713512383', extensions), 'test')

    def test_filter_outgoing_number(self):
        self.assertFalse(util.filter_outgoing_number('+911'))
        self.assertFalse(util.filter_outgoing_number('+15035551212'))
        # Mexico City Anthropological Museum
        self.assertFalse(
            util.filter_outgoing_number('+525555536266'))

    @mock.patch.object(util, 'metric')
    def test_dial_pstn(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'})
        response = util.dial_pstn(request, {})
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response>'
            '<Dial action="https://host/metric_dialer_status" '
            'answerOnBridge="true" callerId="+19713512383">'
            '<Number>+15035551212</Number></Dial></Response>')

    @mock.patch.object(util, 'metric')
    def test_dial_sip(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'},
        context={'domainPrefix':'prod'})
        response = util.dial_sip(request, {})
        self.assertEqual(
            str(response),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true"><Sip>sip:outgoing_safe@futel-prod.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>')


if __name__ == '__main__':
    unittest.main()
