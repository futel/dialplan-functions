from unittest import mock, TestCase
import dial_pstn


out = {'headers':
       {'Content-Type': 'text/xml'},
       'statusCode': 200,
       'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial '
       'action="api_host/api/v1/web/namespace/dialplans/metric_dialer_status" '
       'answerOnBridge="true" callerId="+19713512383"><Number>+15035551212</Number></Dial></Response>'}


class TestDialPstn(TestCase):

    def test_normalize_number(self):
        self.assertEqual(dial_pstn.normalize_number('+15035551212'), '+15035551212')
        self.assertEqual(dial_pstn.normalize_number('15035551212'), '+15035551212')
        self.assertEqual(dial_pstn.normalize_number('5035551212'), '+15035551212')
        self.assertEqual(dial_pstn.normalize_number('+01115035551212'), '+15035551212')
        self.assertEqual(dial_pstn.normalize_number('01115035551212'), '+15035551212')
        self.assertEqual(dial_pstn.normalize_number('+911'), '+911')
        self.assertEqual(dial_pstn.normalize_number('911'), '+911')

    def test_dial_pstn(self):
        event = {'to_uri': 'sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com',
                 'from_uri': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = dial_pstn.dial_pstn(event, context)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
