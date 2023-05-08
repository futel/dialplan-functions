from unittest import mock, TestCase
import dial_sip


out = {'headers':
       {'Content-Type': 'text/xml'},
       'statusCode': 200,
       'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial '
       'action="api_host/api/v1/web/namespace/dialplans/metric_dialer_status" '
       'answerOnBridge="true">'
       '<Sip>sip:operator@futel-stage.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>'}


class TestDialSip(TestCase):

    def test_foo(self):
        event = {'to_extension': '0',
                 'from_uri': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = dial_sip.dial_sip(event, context)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
