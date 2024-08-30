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

    def test_publish_twilio_error(self):
        self.assertTrue(
            metric.publish_twilio_error(
                'foo-bar',
                {'resource_sid': 'foo',
                 'service_sid': None,
                 'error_code': '21609',
                 'more_info': {
                     'Msg': 'Invalid Url for callSid: bar invalid statusCallbackUrl: https://{baz}.dialplans.phu73l.net/metric_dialer_status',
                     'invalidStatusCallbackUrl': 'https://{baz}.dialplans.phu73l.net/metric_dialer_status',
                     'ErrorCode': '21609',
                     'LogLevel': 'WARNING'},
                 'webhook': {
                     'type': 'application/json',
                     'request': {
                         'url': 'sip:demo-one@direct-futel-stage.sip.twilio.com',
                         'method': None,
                         'headers': {},
                         'parameters': {}},
                     'response': {
                         'status_code': None,
                         'headers': {},
                         'body': None}}},
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
