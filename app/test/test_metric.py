from unittest import mock, TestCase

from chalicelib import metric


request = mock.Mock(
    post_fields={
        'SipDomain': 'direct-futel-prod.sip.twilio.com',
        'From': 'sip:bottles-and-cans-one@direct-futel-prod.sip.twilio.com'},
    context={'domainPrefix':'prod'})
env = {
    'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
    'sns_client': mock.Mock()}


class TestMetric(TestCase):

    def test_publish(self):
        self.assertTrue(
            metric.publish('user_event', request, env))

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
