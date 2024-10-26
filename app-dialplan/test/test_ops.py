from unittest import mock, TestCase

from chalicelib import ops

env = {#'AWS_LOGS_TOPIC_ARN': 'AWS_LOGS_TOPIC_ARN',
       'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
       'TWILIO_ACCOUNT_SID': 'TWILIO_ACCOUNT_SID',
       'TWILIO_AUTH_TOKEN': 'TWILIO_AUTH_TOKEN',
       'sns_client': mock.Mock(),
       'stage': 'prod'}

class TestOps(TestCase):

    def test_log(self):#, _mock_metric):
        request = mock.Mock(
            context={'domainPrefix':'prod'},
            post_fields={
                'AccountSid': 'TWILIO_ACCOUNT_SID',
                'Payload': '{"resource_sid":"CA8339b5eb12c2b5bcd3e5e21dd836855a","service_sid":null,"error_code":"32009","more_info":{"Msg":"Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered","ErrorCode":"32009,Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered","LogLevel":"WARNING"},"webhook":{"type":"application/json","request":{"url":"sip:landline@direct-futel-prod.sip.twilio.com","method":"INVITE","headers":{},"parameters":{"To":"sip:landline@direct-futel-prod.sip.twilio.com"}},"response":{"status_code":null,"headers":{},"body":null}}}'})
        got = ops.log(request, env)
        self.assertEqual(got, None)
