from unittest import mock, TestCase

import dial_pstn
import test_util


out = {'headers':
       {'Content-Type': 'text/xml'},
       'statusCode': 200,
       'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial '
       'action="api_host/api/v1/web/namespace/dialers/metric_dialer_status" '
       'answerOnBridge="true" callerId="+19713512383"><Number>+15035551212</Number></Dial></Response>'}


class TestDialPstn(TestCase):

    def test_filter_outgoing_number(self):
        self.assertFalse(dial_pstn.filter_outgoing_number('+911'))
        self.assertFalse(dial_pstn.filter_outgoing_number('+15035551212'))
        # Mexico City Anthropological Museum
        self.assertFalse(
            dial_pstn.filter_outgoing_number('+525555536266'))

    @mock.patch.object(dial_pstn, 'metric')
    def test_dial_pstn(self, _mock_metric):
        event = {
            'To': 'sip:5035551212@direct-futel-nonemergency-stage.sip.twilio.com',
            'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = dial_pstn.dial_pstn(event, context, env)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
