from unittest import mock, TestCase
import dial_sip_e164


out={'headers':
     {'Content-Type': 'text/xml'},
     'statusCode': 200,
     'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="api_host/api/v1/web/namespace/dialplans/metric_dialer_status" answerOnBridge="true" callerId="5035551212"><Sip>sip:test@direct-futel-nonemergency-stage.sip.us1.twilio.com;</Sip></Dial></Response>'}


class TestDialSip(TestCase):

    def test_foo(self):
        event = {'to_number': '9713512383', 'from_number': '5035551212'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = dial_sip_e164.dial_sip_e164(event, context)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
