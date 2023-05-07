from unittest import mock, TestCase
import dial_pstn


out = {'headers':
       {'Content-Type': 'text/xml'},
       'statusCode': 200,
       'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial '
       'action="api_host/api/v1/web/namespace/dialplans/metric_dialer_status" '
       'answerOnBridge="true" callerId="+19713512383"><Number>to_number</Number></Dial></Response>'}


class TestDialPstn(TestCase):

    def test_foo(self):
        event = {'to_number': 'to_number', 'from_uri': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = dial_pstn.dial_pstn(event, context)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
