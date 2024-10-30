from unittest import mock, TestCase

from chalicelib import metric


request = mock.Mock(
    post_fields={
        'SipDomain': 'direct-futel-prod.sip.twilio.com',
        'From': 'sip:bottles-and-cans-one@direct-futel-prod.sip.twilio.com'},
    context={'domainPrefix':'prod'})
env = {
    'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
    'sns_client': mock.Mock(),
    'stage':'prod'}



class TestMetric(TestCase):

    def test_publish(self):
        self.assertTrue(
            metric.publish('user_event', "user", env))

    def test_publish_twilio_error_foo(self):
        self.assertTrue(
            metric.publish_twilio_error(
                'foo-bar',
                {'url': 'sip:demo-one@direct-futel-stage.sip.twilio.com',
                 'method': None,
                 'headers': {},
                 'parameters': {}},
                env))

    def test_publish_twilio_error_bar(self):
        message = {'url': 'http://10.209.67.130:8080/ivr/outgoing_operator_operator?parent=outgoing_operator_operator&lang=en&iteration=0&stanza=menu', 'method': 'POST', 'headers': {}, 'parameters': {'ApiVersion': '2010-04-01', 'CalledZip': '97114', 'Called': '+1503xxxxxxx', 'CallStatus': 'in-progress', 'CalledCity': 'CARLTON', 'From': '+15034448615', 'ToState': 'OR', 'CallerCountry': 'US', 'Direction': 'outbound-api', 'AccountSid': 'ACccee506a7e232c9b6b17175c9e54860c', 'CalledCountry': 'US', 'CallerCity': 'BEAVERTON', 'CallerState': 'OR', 'Caller': '+15034448615', 'FromCountry': 'US', 'ToCity': 'CARLTON', 'ToZip': '97114', 'FromCity': 'BEAVERTON', 'CalledState': 'OR', 'To': '+1503xxxxxxx', 'CallSid': 'CA96ec5e33405afd1a43935f0039d1a0af', 'FromZip': '97229', 'ToCountry': 'US', 'CallerZip': '97229', 'FromState': 'OR'}}
        self.assertTrue(
            metric.publish_twilio_error(
                'foo-bar',
                message,
                env))

    def test_event_to_message(self):
        out = {
            "timestamp": "2023-05-11T22:36:13.000489",
            "hostname": "hostname",
            "event": {
                "Event": "UserEvent",
                "endpoint": "endpoint",
                "Channel": "endpoint",
                "UserEvent": "user_event"}}
        got = metric._event_to_message(
            'endpoint', 'user_event', 'hostname')
        del out['timestamp']
        del got['timestamp']
        self.assertEqual(got, out)


if __name__ == '__main__':
    unittest.main()
