from unittest import mock, TestCase

from chalicelib import dialers
from chalicelib import ivr_destinations
from chalicelib import sns_client
from chalicelib import env_util
from chalicelib import util

env = {'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
       'ASSET_HOST': 'ASSET_HOST',
       'TWILIO_ACCOUNT_SID': 'TWILIO_ACCOUNT_SID',
       'TWILIO_AUTH_TOKEN': 'TWILIO_AUTH_TOKEN',
       'extensions': env_util.get_extensions(),
       'ivrs': env_util.get_ivrs(),
       'operator_numbers': ['foo', 'bar'],
       'sns_client': mock.Mock(),
       'stage':'stage'}

outgoing_safe_body = '<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>/ivr</Redirect></Response>'

class TestDialOutgoing(TestCase):

    @mock.patch.object(dialers, 'metric')
    def test_dial_outgoing_local(self, _mock_metric):
        # test extension redirects to local context.
        request = mock.Mock(
            headers={'host': 'host'},
            from_user='test-one',
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-nonemergency-stage.sip.twilio.com'},
            query_params={},
            context={'domainPrefix':'prod'})
        got = dialers.dial_outgoing(request, env)
        self.assertEqual(str(got), outgoing_safe_body)

    # # We are phasing these out.
    # @mock.patch.object(dialers, 'metric')
    # def test_dial_outgoing_remote(self, _mock_metrici):
    #     # demo extension redirects to SIP URI call.
    #     request = mock.Mock(
    #         headers={'host': 'host'},
    #         query_params={},
    #         post_fields={
    #             'SipDomain': 'direct-futel-prod.sip.twilio.com',
    #             'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
    #             'From': 'sip:alleymaple@direct-futel-nonemergency-stage.sip.twilio.com'},
    #         context={'domainPrefix':'prod'})
    #     got = dialers.dial_outgoing(request, env)
    #     self.assertEqual(
    #         str(got),
    #         '<?xml version="1.0" encoding="UTF-8"?><Response><Dial answerOnBridge="true"><Sip>sip:outgoing_portland@futel-prod.phu73l.net;region=us2?x-callerid=+15034681337&amp;x-enableemergency=false</Sip></Dial></Response>')


class TestDialSipE164(TestCase):

    @mock.patch.object(dialers, 'metric')
    def test_dial_sip_e164(self, _mock_metric):
        request = mock.Mock(
            from_user='hot-leet',
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': '9713512383',
                'From': '5035551212'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_sip_e164(request, env)
        self.assertEqual(
            str(got),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>/dial_extension/test-one</Redirect></Response>')


class TestIvr(TestCase):
    @mock.patch.object(dialers, 'metric')
    def test_ivr_no_context(self, _mock_metric):
        request = mock.Mock(
            from_user='test-one',
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com'},
            query_params={},
            context={'domainPrefix':'prod'})
        got = dialers.ivr('xxx', request, env)
        # Smoke test.

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:outgoing_portland@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com'},
            query_params={},
            context={'domainPrefix':'prod'})
        got = dialers.ivr('outgoing_portland', request, env)
        # Smoke test.

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context_star(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*'},
            context={'domainPrefix':'prod'})

        got = dialers.ivr('outgoing_portland', request, env)
        # Smoke test.


class TestEnqueueOperatorWait(TestCase):

    @mock.patch.object(dialers, 'Client')
    @mock.patch.object(ivr_destinations, 'Client')
    def test_enqueue_operator_wait(self, _mock1, _mock2):
        request = mock.Mock(
            from_user='test-one',
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*'},
            context={'domainPrefix':'prod'})
        got = dialers.enqueue_operator_wait(request, env)
        # Smoke test.


class OutgoingOperatorLeave(TestCase):

    @mock.patch.object(dialers, 'Client')
    @mock.patch.object(ivr_destinations, 'Client')
    def test_outgoing_operator_leave(self, _mock1, _mock2):
        request = mock.Mock(
            from_user='test-one',
            headers={'host': 'host'},
            post_fields={
                'CallSid': 'CallSid',
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*',
                'QueueResult': 'QueueResult'},
            context={'domainPrefix': 'prod'},
            query_params={'lang': 'en'})
        got = dialers.outgoing_operator_leave(request, env)
        # Smoke test.


if __name__ == '__main__':
    unittest.main()
