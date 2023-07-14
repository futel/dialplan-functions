from unittest import mock, TestCase

from chalicelib import sns_client

#request = mock.Mock(raw_body=b'AccountSid=SID&ApiVersion=2010-04-01&CallSid=SID&CallStatus=ringing&Called=sip%3ANUMBER%40direct-futel-nonemergency-dev.sip.twilio.com&Caller=sip%3AEXTENSION%40direct-futel-nonemergency-dev.sip.twilio.com&Direction=inbound&From=sip%3AEXTENSION%40direct-futel-nonemergency-dev.sip.twilio.com&SipCallId=ID&SipDomain=direct-futel-nonemergency-dev.sip.twilio.com&SipDomainSid=SID&SipSourceIp=IP&To=sip%3ANUMBER%40direct-futel-nonemergency-dev.sip.twilio.com')
request = mock.Mock(post_fields = {'SipDomain': 'direct-futel-prod.sip.twilio.com'})

class TestSnsClient(TestCase):

    @mock.patch.object(sns_client, 'boto3')
    def test_publish(self, _mock_boto3):
        self.assertTrue(
            sns_client.publish('endpoint', 'user_event', request))

    def test_event_to_message(self):
        out = {
            "timestamp": "2023-05-11T22:36:13.000489",
            "hostname": "hostname",
            "event": {
                "Event": "UserEvent",
                "endpoint": "endpoint",
                "Channel": "endpoint",
                "UserEvent": "user_event"}}
        got = sns_client.event_to_message(
            'endpoint', 'user_event', 'hostname')
        del out['timestamp']
        del got['timestamp']
        self.assertEqual(got, out)

if __name__ == '__main__':
    unittest.main()
