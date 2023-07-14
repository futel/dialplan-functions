from unittest import mock, TestCase

import ivr
import test_util


class TestIvr(TestCase):

    @mock.patch.object(ivr, 'metric')
    def test_ivr_no_context(self, _mock_metric):
        event = {
            'To':
            'sip:xyzzy@direct-futel-nonemergency-stage.sip.twilio.com',
            'From':
            'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = ivr.ivr(event, context, env)
        # Smoke test.

    @mock.patch.object(ivr, 'metric')
    def test_ivr_context(self, _mock_metric):
        event = {
            'To':
            'sip:xyzzy@direct-futel-nonemergency-stage.sip.twilio.com',
            'From':
            'sip:test@direct-futel-nonemergency-stage.sip.twilio.com',
            'context': 'outgoing_portland'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = ivr.ivr(event, context, env)
        # Smoke test.

    @mock.patch.object(ivr, 'metric')
    def test_ivr_context_star(self, _mock_metric):
        event = {
            'To':
            'sip:xyzzy@direct-futel-nonemergency-stage.sip.twilio.com',
            'From':
            'sip:test@direct-futel-nonemergency-stage.sip.twilio.com',
            'context': 'outgoing_portland',
            'Digits': '*'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = ivr.ivr(event, context, env)
        # Smoke test.


if __name__ == '__main__':
    unittest.main()
