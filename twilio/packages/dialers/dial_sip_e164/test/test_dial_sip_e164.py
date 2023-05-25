from unittest import mock, TestCase

import dial_sip_e164
import test_util


out={'headers':
     {'Content-Type': 'text/xml'},
     'statusCode': 200,
     'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="api_host/api/v1/web/namespace/dialers/metric_dialer_status" answerOnBridge="true" callerId="5035551212"><Sip>sip:test@direct-futel-nonemergency-INSTANCE.sip.us1.twilio.com;</Sip></Dial></Response>'}


class TestDialSipE164(TestCase):

    @mock.patch.object(dial_sip_e164, 'metric')
    def test_dial_sip_e164(self, _mock_metric):
        event = {'To': '9713512383', 'From': '5035551212'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = dial_sip_e164.dial_sip_e164(event, context, env)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
