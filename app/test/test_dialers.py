from unittest import mock, TestCase

from chalicelib import dialers
from chalicelib import sns_client
from chalicelib import env_util
from chalicelib import util

env = {'AWS_TOPIC_ARN': 'AWS_TOPIC_ARN',
       'ASSET_HOST': 'ASSET_HOST',
       'extensions': {
           "alleymaple": {
               "outgoing": "outgoing_portland",
               "caller_id": "+15034681337",
               "enable_emergency": False,
               "local_outgoing": False
           },
           "demo": {
               "outgoing": "outgoing_safe",
               "caller_id": "+15038945775",
               "enable_emergency": False,
               "local_outgoing": True
           },
           "test": {
               "outgoing": "outgoing_safe",
               "caller_id": "+19713512383",
               "enable_emergency": False,
               "local_outgoing": True
           }},
       'ivrs': {
           "outgoing_portland": {
               "name": "outgoing_portland",
               "pre_callable": "friction",
               "intro_statements": ["para-espanol", "oprima-estrella"],
               "menu_entries": [
                   ["to-make-a-call", "outgoing-dialtone-wrapper"],
                   ["for-voicemail", "voicemail_outgoing"],
                   ["for-the-directory", "directory_portland"],
                   ["for-utilities", "utilities_portland"],
                   ["for-the-fewtel-community", "community_outgoing"],
                   ["for-community-services", "community_services_oregon"],
                   ["for-the-telecommunications-network", "network"],
                   None,
                   [None, "call_911_9"]],
               "other_menu_entries": [
                   ["for-the-operator", 0, "operator"]],
               "statement_dir": "outgoing"},
           "outgoing_safe": {
               "name": "outgoing_safe",
               "pre_callable": "friction",
               "intro_statements": ["para-espanol", "oprima-estrella"],
               "menu_entries": [
                   ["to-make-a-call", "outgoing-dialtone-wrapper"],
                   ["for-voicemail", "voicemail_outgoing"],
                   ["for-the-directory", "directory_safe"],
                   ["for-utilities", "utilities_portland"],
                   ["for-the-fewtel-community", "community_outgoing"],
                   ["for-the-telecommunications-network", "network"],
                   None,
                   None,
                   None],
               "other_menu_entries": [
                   ["for-the-operator", 0, "operator"]],
               "statement_dir": "outgoing"}},
       'sns_client': mock.Mock()}



# whatever
outgoing_safe_body = '<?xml version="1.0" encoding="UTF-8"?><Response><Gather action="https://host/ivr?context=outgoing_safe&amp;lang=en&amp;parent=outgoing_safe" numDigits="1" timeout="0"><Play>https://ASSET_HOST/en/outgoing/para-espanol.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/oprima-estrella.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/to-make-a-call.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-one.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-voicemail.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-two.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-directory.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-three.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-utilities.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-four.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-fewtel-community.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-five.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-telecommunications-network.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/press-six.ulaw</Play><Play>https://ASSET_HOST/en/outgoing/for-the-operator.ulaw</Play></Gather></Response>'


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
        self.assertEqual(str(got), outgoing_safe_body)

    @mock.patch.object(util, 'metric')
    @mock.patch.object(dialers, 'metric')
    def test_dial_outgoing_remote(self, _mock_metric, _mock_metric2):
        # demo extension redirects to SIP URI call.
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
                'From': 'sip:alleymaple@direct-futel-nonemergency-stage.sip.twilio.com'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_outgoing(request, env)
        self.assertEqual(
            str(got),
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://host/metric_dialer_status" answerOnBridge="true"><Sip>sip:outgoing_portland@futel-prod.phu73l.net;region=us2?x-callerid=+15034681337&amp;x-enableemergency=false</Sip></Dial></Response>')


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
        got = dialers.dial_sip_e164(request, env)
        self.assertEqual(
            str(got),
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
        got = dialers.request_to_metric_events(request, env)
        self.assertEqual(
            got, ('outgoing_call', 'outgoing_dialstatus_completed_test'))

    def test_request_to_metric_events_incoming(self):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': '+19713512383',
                'From': '+19713512383',
                'DialCallStatus': 'completed'})
        got = dialers.request_to_metric_events(request, env)
        self.assertEqual(
            got, ('incoming_call', 'incoming_dialstatus_completed_test'))


class TestIvr(TestCase):
    @mock.patch.object(dialers, 'metric')
    def test_ivr_no_context(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test@direct-futel-prod.sip.twilio.com'},
        context={'domainPrefix':'prod'})
        got = dialers.ivr(request, env)
        # Smoke test.

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test@direct-futel-prod.sip.twilio.com',
                'context': 'outgoing_portland'},
        context={'domainPrefix':'prod'})
        got = dialers.ivr(request, env)
        # Smoke test.

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context_star(self, _mock_metric):
        request = mock.Mock(
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test@direct-futel-prod.sip.twilio.com',
                'context': 'outgoing_portland',
                'Digits': '*'},
            context={'domainPrefix':'prod'})

        got = dialers.ivr(request, env)
        # Smoke test.


if __name__ == '__main__':
    unittest.main()
