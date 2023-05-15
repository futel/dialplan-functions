from unittest import mock, TestCase
import dial_outgoing


out = {
    'headers': {'Content-Type': 'text/xml'},
    'statusCode': 200,
    'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>api_host/api/v1/web/namespace/dialplans/dial_sip?to_uri=sip%3A%2523%40direct-futel-nonemergency-stage.sip.twilio.com&amp;from_uri=sip%3Atest%40direct-futel-nonemergency-stage.sip.twilio.com</Redirect></Response>'}


class TestDialOutgoing(TestCase):

    def test_foo(self):
        event = {
            'to_uri': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
            'from_uri': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = dial_outgoing.dial_outgoing(event, context)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
