from unittest import mock, TestCase

from chalicelib import dialers
from chalicelib import sns_client
from chalicelib import util

env = {'AWS_TOPIC_ARN': 'AWS_TOPIC_ARN'}


class TestDialOutgoing(TestCase):

    @mock.patch.object(util, 'metric')
    @mock.patch.object(dialers, 'metric')
    def test_dial_outgoing_local(self, _mock_metric, _mock_metric2):
        # test extension redirects to local context.
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_outgoing(request, env)
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.headers, {'Content-Type': 'text/xml'})
        self.assertEqual(
            got.body,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true"><Sip>sip:outgoing_safe@futel-prod.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>')

    @mock.patch.object(util, 'metric')
    @mock.patch.object(dialers, 'metric')
    def test_dial_outgoing_remote(self, _mock_metric, _mock_metric2):
        # demo extension redirects to SIP URI call.
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:demo@direct-futel-nonemergency-stage.sip.twilio.com'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_outgoing(request, env)
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.headers, {'Content-Type': 'text/xml'})
        self.assertEqual(
            got.body,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true"><Sip>sip:outgoing_safe@futel-prod.phu73l.net;region=us2?x-callerid=+15038945775&amp;x-enableemergency=false</Sip></Dial></Response>')


class TestDialSipE164(TestCase):

    @mock.patch.object(dialers, 'metric')
    def test_dial_sip_e164(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': '9713512383',
                'From': '5035551212'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_sip_e164(request, {})
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.headers, {'Content-Type': 'text/xml'})
        self.assertEqual(
            got.body,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true" callerId="5035551212"><Sip>sip:test@direct-futel-nonemergency-prod.sip.twilio.com;</Sip></Dial></Response>')


class TestMetricDialerStatus(TestCase):

    def test_request_to_metric_events_outgoing(self):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'To',
                'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com',
                'DialCallStatus': 'completed'})
        got = dialers.request_to_metric_events(request)
        self.assertEqual(
            got,
            ({'endpoint': 'test', 'user_event': 'outgoing_call'},
             {'endpoint': 'test', 'user_event': 'outgoing_dialstatus_completed_test'}))

    def test_request_to_metric_events_incoming(self):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': '+19713512383',
                'From': '+19713512383',
                'DialCallStatus': 'completed'})
        got = dialers.request_to_metric_events(request)
        self.assertEqual(
            got,
            ({'endpoint': 'test', 'user_event': 'incoming_call'},
             {'endpoint': 'test', 'user_event': 'incoming_dialstatus_completed_test'}))


if __name__ == '__main__':
    unittest.main()
