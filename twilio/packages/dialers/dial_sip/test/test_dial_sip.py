from unittest import mock, TestCase

import dial_sip
import test_util


out = {'headers':
       {'Content-Type': 'text/xml'},
       'statusCode': 200,
       'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial '
       'action="api_host/api/v1/web/namespace/dialers/metric_dialer_status" '
       'answerOnBridge="true">'
       '<Sip>sip:outgoing_safe@futel-INSTANCE.phu73l.net;region=us2?x-callerid=+19713512383&amp;x-enableemergency=false</Sip></Dial></Response>'}


class TestDialSip(TestCase):

    @mock.patch.object(dial_sip, 'metric')
    def test_dial_sip(self, _mock_metric):
        event = {
            'To': 'sip:%23@direct-futel-nonemergency-stage.sip.twilio.com',
            'From': 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        env = test_util.MockDict()
        got = dial_sip.dial_sip(event, context, env)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
