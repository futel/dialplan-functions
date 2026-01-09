from unittest import mock, TestCase

from chalicelib import dialers
from chalicelib import ivr_destinations
from chalicelib import sns_client
from chalicelib import env_util
from chalicelib import util

# Mock a client with unpopulated operator queues, ie an empty iterator.
twilio_client = mock.Mock()
twilio_client.queues = mock.MagicMock()

env = {'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
       'ASSET_HOST': 'ASSET_HOST',
       'extensions': env_util._get_extensions(),
       'ivrs': env_util._get_ivrs(),
       'operator_numbers': ['foo', 'bar'],
       'sns_client': mock.Mock(),
       'stage':'stage',
       'twilio_client': twilio_client}

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
                'To': 'sip:%23@direct-futel-stage.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-stage.sip.twilio.com'},
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
    #             'To': 'sip:%23@direct-futel-stage.sip.twilio.com',
    #             'From': 'sip:alleymaple@direct-futel-stage.sip.twilio.com'},
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
                'To': '15034449412',
                'From': '5035551212'},
            context={'domainPrefix':'prod'})
        got = dialers.dial_sip_e164(request, env)
        self.assertEqual(
            str(got),
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Response><Redirect>/dial_extension/ainsworth</Redirect></Response>')


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
    def test_ivr_context_digit_star_no_lang(self, _mock_metric):
        """
        A star digit given to ivr_context with no lang query_param
        returns a redirect with the 'es' lang.
        """
        request = mock.Mock(
            context={'domainPrefix':'prod'},
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*'},
                query_params={})

        got = dialers.ivr('outgoing_portland', request, env)
        # Q&D check for a substring, hope the lang query param is correctly
        # formatted in there.
        self.assertIn('lang=es', got)

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context_digit_star_en(self, _mock_metric):
        """
        A star digit given to ivr_context with the en lang query_param
        returns a redirect with the 'es' lang.
        """
        request = mock.Mock(
            context={'domainPrefix':'prod'},
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*'},
                query_params={'lang': 'en'})

        got = dialers.ivr('outgoing_portland', request, env)
        # Q&D check for a substring, hope the lang query param is correctly
        # formatted in there.
        self.assertIn('lang=es', got)

    @mock.patch.object(dialers, 'metric')
    def test_ivr_context_digit_star_es(self, _mock_metric):
        """
        A star digit given to ivr_context with the es lang query_param
        returns a redirect with the 'en' lang.
        """
        request = mock.Mock(
            context={'domainPrefix':'prod'},
            headers={'host': 'host'},
            post_fields={
                'SipDomain': 'direct-futel-prod.sip.twilio.com',
                'To': 'sip:xyzzy@direct-futel-prod.sip.twilio.com',
                'From': 'sip:test-one@direct-futel-prod.sip.twilio.com',
                'Digits': '*'},
                query_params={'lang': 'es'})

        got = dialers.ivr('outgoing_portland', request, env)
        # Q&D check for a substring, hope the lang query param is correctly
        # formatted in there.
        self.assertIn('lang=en', got)


class TestEnqueueOperatorWait(TestCase):

    def test_enqueue_operator_wait(self):
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

    def test_outgoing_operator_leave(self):
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


class TestDialSip(TestCase):
    """Test cases for dialers._dial_sip()"""

    def test_dial_sip_single_extension(self):
        """Test _dial_sip with a single extension."""
        request = mock.Mock()
        extension_names = ['test-one']
        from_number = '+15034681337'

        got = dialers._dial_sip(extension_names, from_number, request, env)

        # Verify the response is valid TwiML string
        self.assertIsInstance(got, str)
        self.assertIn('<Response>', got)
        self.assertIn('</Response>', got)
        self.assertIn('<Dial', got)
        self.assertIn('</Dial>', got)

        # Verify caller_id is set correctly
        self.assertIn('callerId="+15034681337"', got)

        # Verify answer_on_bridge is set
        self.assertIn('answerOnBridge="true"', got)

        # Verify time limit is set
        self.assertIn('timeLimit="3600"', got)

        # Verify action callback is set
        self.assertIn('action="/ops/call_status_outgoing"', got)

        # Verify the SIP URI is correct
        sip_domain = dialers._get_sip_domain(env)
        expected_sip_uri = f'sip:test-one@{sip_domain}'
        self.assertIn(expected_sip_uri, got)
        self.assertIn('<Sip>', got)
        self.assertIn('</Sip>', got)

    def test_dial_sip_multiple_extensions(self):
        """Test _dial_sip with multiple extensions."""
        request = mock.Mock()
        extension_names = ['test-one', 'test-two', 'test-three']
        from_number = '+15034681337'

        got = dialers._dial_sip(extension_names, from_number, request, env)

        # Verify the response is valid TwiML
        self.assertIsInstance(got, str)
        self.assertIn('<Response>', got)
        self.assertIn('<Dial', got)

        # Verify all three extensions are included
        sip_domain = dialers._get_sip_domain(env)
        for extension_name in extension_names:
            expected_sip_uri = f'sip:{extension_name}@{sip_domain}'
            self.assertIn(expected_sip_uri, got)

        # Count the number of <Sip> tags (should be 3)
        sip_count = got.count('<Sip>')
        self.assertEqual(sip_count, 3)

    def test_dial_sip_different_from_numbers(self):
        """Test _dial_sip with different caller IDs."""
        request = mock.Mock()
        extension_names = ['test-one']

        # Test with different from_numbers
        from_numbers = ['+15034681337', '+15551234567', '2025551234']
        for from_number in from_numbers:
            got = dialers._dial_sip(extension_names, from_number, request, env)
            self.assertIn(f'callerId="{from_number}"', got)

    def test_dial_sip_uses_correct_sip_domain(self):
        """Test _dial_sip uses the correct SIP domain from environment."""
        request = mock.Mock()
        extension_names = ['extension-alpha']
        from_number = '+15034681337'

        got = dialers._dial_sip(extension_names, from_number, request, env)

        # Get the expected domain
        sip_domain = dialers._get_sip_domain(env)

        # Verify it's used in the SIP URI
        self.assertIn(f'@{sip_domain}', got)

        # Verify it matches the expected format
        self.assertIn('direct-futel', sip_domain)
        self.assertIn('sip.twilio.com', sip_domain)


if __name__ == '__main__':
    unittest.main()
